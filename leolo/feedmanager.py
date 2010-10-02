import threading
import re
from datetime import timedelta, datetime
from collections import deque
import xml.parsers.expat
import feedparser
import settings
from downloaders import HeadDownloader, Downloader
from models import Feed, Entry
from logger import Logger
from time import sleep

feedparser._HTMLSanitizer.acceptable_elements = ['a', 'abbr', 'acronym',
   'address', 'area', 'b', 'big', 'blockquote', 'br', 'button', 'caption',
   'center', 'cite', 'code', 'col', 'colgroup', 'dd', 'del', 'dfn', 'dir',
   'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'font', 'form', 'h1', 'h2',
   'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'input', 'ins', 'kbd', 'label',
   'legend', 'li', 'map', 'menu', 'ol', 'optgroup', 'option', 'p',
   'param', 'pre', 'q', 's', 'samp', 'select', 'small', 'span', 'strike',
   'strong', 'sub', 'sup', 'table', 'tbody', 'td', 'textarea', 'tfoot', 'th',
   'thead', 'tr', 'tt', 'u', 'ul', 'var']

def date_compare(x, y):
    """
    Function to order feeds by last check date.
    """
    if not x.last_check:
        return -1
    if not y.last_check:
        return 1
    if x.last_check > y.last_check:
        return 1
    elif x.last_check == y.last_check:
        return 0
    else:
        return -1

def threadsafe_function(fn):
    """
    Decorator making sure that the decorated function is thread safe.
    http://stackoverflow.com/questions/1072821/
    """
    lock = threading.Lock()
    def new(*args, **kwargs):
        lock.acquire()
        try:
            r = fn(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            lock.release()
        return r
    return new

class FeedManager(object):
    """
    This class takes care about extracting all relevant information from
    feeds using Feedparser and creating all the necessary objects.
    """
    TIMEOUT = 10 # timeout in seconds. Static class variable

    def __init__(self, feeds=None):
        """
        Constructor. Receives a list of feeds.
        """
        self.feeds = feeds
        self.logger = Logger("FeedManager")
        self.count_downloading = 0 # items currently being downloaded
    
    def _check_entries(self, feed):
        """
        Given a Feed object instance, returns a list with new entries.
        If there are no new entries, then the list will be empty: [].
        """
        d = feedparser.parse(feed.url)
        entries = []
        try:
            if feed.last_entrylink == d.entries[0].link:
                return []
        except IndexError, error:
            self.logger.info("Illformed XML file '%s. Details:\
                             \n%s" % (feed.url, error))
            return []
        # For every entry
        for i in range (len(d.entries)):
            if feed.last_entrylink == d.entries[i].link:
                break
            # Create entry object
            entries.append(self._entry_factory(d.entries[i]))

        feed.last_entrylink = d.entries[0].link
        return entries

    def check_feed(self, feedurl, check_feed):
        """
        Checks that feed exists and it's well formed.
        'check_feed' could be True or False.
        Returns two variables if everything was OK: feed's title, site's url.
        Returns None if there was an error.
        """
        # Now the feed will be downloaded
        dl = Downloader(feedurl)
        dl.start()
        dl.join()
        site = None

        # Any error while downloading
        if dl.error:
            self.logger.info("Couldn't retrieve feed '%s'. Details:\
                             \n%s" % (feedurl, dl.error))
            return None

        # Check well-formed XML
        if check_feed:
            if not FeedManager._valid_feed(dl.response.read()):
                self.logger.info("'%s' is not valid XML file!" % feedurl)
                dl.response.close()
                return None

        try:
            # Parse feed
            d = feedparser.parse(feedurl)
            # Clean title
            title = re.sub("\s+", " ", d.feed.title)
            return title, d.feed.link
        except:
            s = "Error while adding '%s'. Probably not a valid XML" \
                " file. Check the URL, please." % feedurl
            self.logger.info(s)
            return None

    @staticmethod
    def _entry_factory(entry):
        """
        Gets a Feedparser entry and creates an Entry object.
        Returns the Entry object created.
        """
        # Get all enclosures links
        enclosures = []
        try:
            for i in range(len(entry.enclosures)):
                enclosures.append(entry.enclosures[i].href)
        except:
            pass
        # Sometimes we only find summary or description tags (or both)
        content1 = ""
        content2 = ""
        content3 = ""
        try:
            content1 = entry.summary
        except AttributeError:
            pass
        try:
            content2 = entry.description
        except AttributeError:
            pass
        try:
            content3 = entry.content[0].value
        except AttributeError:
            pass
        # Gets the longest content
        if len(content1) > len(content2):
            content = content1
        else:
            content = content2
        if len(content) < len(content3):
            content = content3
        e = Entry(entry.link, entry.title, content, enclosures)
        return e

    @staticmethod
    def mark_as_read(feed):
        """
        Given a Feed object instance, marks older links as read, so that only
        new entries will be taken into account.
        """
        d = feedparser.parse(feed.url)
        feed.last_entrylink = d.entries[0].link

    def process_feed(self, hdl):
        """
        Callback to be called by HeadDownloader when the HEAD downloading
        has finished.
        """
        self.update_count_downloading(-1)
        if hdl.error:
            self.logger.info("Couldn't retrieve header '%s'. Details:\
                             \n%s" % (hdl.url, hdl.error))
            return

        for feed in self.feeds:
            if feed.url == hdl.url:
                break
        feed.last_check = datetime.now()
        # Check last_modified
        if not feed.last_modified \
           or feed.last_modified != hdl.info["last-modified"]:
            # Download the Feed
            dl = Downloader(feed.url)
            dl.start()
            dl.join(FeedManager.TIMEOUT * 2)
            if dl.is_alive():
                self.logger.info("Time out while getting feed '%s'." % (dl.url))
                return

            # Check and get new entries
            new_entries = self._check_entries(feed)
            # Associate entries with feed and update 'last_modified' field
            feed.entries = new_entries
            feed.last_modified = hdl.info["last-modified"]

    @threadsafe_function
    def update_count_downloading(self, n):
        """
        Must be threadsafe because it's possible that 2 threads read and
        overwrite the variable at the same time, causing problems.
        'n' must be an integer.
        """
        self.count_downloading += n

    def update_feeds(self, minutes, limit):
        """
        Updates all feeds.
        """
        # Order feeds by last check date
        self.feeds.sort(date_compare)
        queue = deque()

        for feed in self.feeds:
            # If the feed wasn't checked or was checked before 'minutes'
            # minutes ago, then download headers
            if not feed.last_check or \
               feed.last_check + timedelta(minutes=minutes) < datetime.now():
                while (self.count_downloading >= settings.PARALLEL_DL):
                    sleep(0.4)
                dl = HeadDownloader(feed.url, self.process_feed)
                dl.start()
                queue.append(dl)
                self.count_downloading += 1 # doesn't need to use the
                                            # threadsafe function
                if limit > 1:
                    limit -= 1
                elif limit == 1:
                    break

        # Joining threads to this main thread
        for dl in queue:
            dl.join(FeedManager.TIMEOUT)
            if dl.is_alive():
                self.logger.info("Time out while getting headers of '%s'." % (dl.url))

    @staticmethod
    def _valid_feed(content):
        """
        Checks that given feed content is a valid XML file.
        Returns True if it's a good file, otherwise False.
        """
        try:
            parser = xml.parsers.expat.ParserCreate()
            parser.Parse(content)
        except Exception:
            return False
        return True

