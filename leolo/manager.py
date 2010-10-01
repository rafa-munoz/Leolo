import re
from logger import Logger
from meta import Session
from models import Site, Feed
from feedmanager import FeedManager
from filter import Filter

# Found in django/forms/fields.py
url_re = re.compile(
    r'^https?://' # http:// or https://
    r'(?:(?:[A-Z0-9-]+\.)+[A-Z]{2,6}|' #domain...
    r'localhost|' #localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
    r'(?::\d+)?' # optional port
    r'(?:/?|/\S+)$', re.IGNORECASE)

class Manager(object):
    """
    Feeds Manager.
    This is the main object to control Leolo. No other classes should be used
    instead.
    """
    def __init__(self):
        """
        Database loading.
        """
        self.sites = [] # list with all sites objects
        self.logger = Logger("Manager")
        self.session = Session()
        self.sites = self.session.query(Site).all() # loading all sites

    def activate_site(self, opt):
        """
        Makes a site active.
        User can pass as 'opt' a site number or feed url.
        """
        self.deactivate_site(opt, False)

    def add_site(self, feedurl, mark_as_read=False):
        """
        Adds a new site.
        'feedurl' is the feed's url.
        If 'mark_as_read' is True, then old entries will be ignored in next
        update. Only new entries from now will be indexed.
        Returns feed's title if everything it's ok, otherwise, None.
        """
        # Check valid url
        if not url_re.search(feedurl):
            s = "Site: '%s' is not a valid url!" % (feedurl)
            self.logger.info(s)
            raise ValueError(s)

        # Check if site already exists in DB, and if it doesn't, a new Site
        # instance is created and saved.
        if not self.session.query(Site, Feed).\
           filter(Site.id==Feed.siteid).filter(Feed.url==feedurl).first():
            fm = FeedManager()
            result = fm.check_feed(feedurl, True)
            if result:
                site = Site(feedurl, result[0], result[1])
                if mark_as_read:
                    FeedManager.mark_as_read(site.feed)
                self.session.save(site)
                self.session.commit()
                self.sites.append(site)
                return result[0]

    def deactivate_site(self, opt, deactivate=True):
        """
        Makes a site inactive.
        User can pass as 'opt' a site number or feed url.
        """
        # By option number
        if isinstance(opt, int):
            try:
                site = self.session.query(Site).filter(Site.id==opt).one()
                feed = self.session.query(Feed).filter(Feed.siteid==opt).one()
                i = 0
                while True:
                    if self.sites[i].feed.url == site.feed.url:
                        if deactivate:
                            self.sites[i].inactive = True
                        else:
                            self.sites[i].inactive = False
                        self.session.commit()
                        break
                    i += 1
            except IndexError:
                act_deact = None
                if deactivate:
                    act_deact = "deactivate"
                else:
                    act_deact = "activate"
                s = "Cannot find to %s site #%s." % (act_deact, str(opt))
                self.logger.error(s)
                return
        # By feed url
        elif isinstance(opt, str):
            i = 0
            while True:
                try:
                    site = self.sites[i]
                    if site.feed.url == opt:
                        if deactivate:
                            self.sites[i].inactive = True
                        else:
                            self.sites[i].inactive = False
                        self.session.commit()
                        break;
                    i += 1
                except IndexError:
                    act_deact = None
                    if deactivate:
                        act_deact = "deactivate"
                    else:
                        act_deact = "activate"
                    s = "Cannot find '%s' to %s." % (str(opt), act_deact)
                    self.logger.error(s)
                    return
        # Error
        else:
            s = "Not a valid site! Use site's feed url or site number."
            self.logger.error(s)
            raise TypeError(s)

    def del_site(self, opt):
        """
        Removes site.
        User can pass as 'opt' a site number or feed url.
        """
        # Del by option number
        if isinstance(opt, int):
            try:
                site = self.session.query(Site).filter(Site.id==opt).one()
                feed = self.session.query(Feed).filter(Feed.siteid==opt).one()
                i = 0
                while True:
                    if self.sites[i].feed.url == site.feed.url:
                        del self.sites[i]
                        break
                    i += 1
                self.session.delete(site)
                self.session.commit()
            except IndexError:
                s = "Cannot find to remove site #" + str(opt) + "."
                self.logger.error(s)
                return
        # Del by feed url
        elif isinstance(opt, str):
            i = 0
            while True:
                try:
                    site = self.sites[i]
                    if site.feed.url == opt:
                        self.session.delete(site)
                        self.session.delete(site.feed)
                        del self.sites[i]
                        self.session.commit()
                        return
                    i += 1
                except IndexError:
                    s = "Cannot find to remove site's feed '" + opt + "'."
                    self.logger.error(s)
                    return
        # Error
        else:
            s = "Not a valid site! Use site's feed url or site number."
            self.logger.error(s)
            raise TypeError(s)

    def del_sites(self):
        """
        Deletes all sites.
        """
        sites = self.session.query(Site).all()
        for site in sites:
            self.session.delete(site)
        del self.sites[:]

    def display_sites(self):
        """
        Returns all sites as a string.
        """
        if len(self.sites) == 0:
            return "No sites yet."

        s = ""
        for (i, site) in enumerate(self.sites):
            if i > 0:
                s += "\n"
            s += "%s" % site
        return s

    def filter(self, q):
        """
        q is the query.
        """
        if not isinstance(q, str):
            s = "filter: invalid query argument. You must use a string."
            self.logger.error(s)
            raise TypeError(s)
        f = Filter(self.sites, q)
        f.apply()

    def get_site(self, opt):
        """
        Gets a site.
        """
        # TODO
        pass

    def get_sites(self):
        """
        Return all sites in a List.
        """
        return self.sites

    def update_sites(self, minutes=20, limit=None):
        """
        Updates all feeds from all sites.
        'minutes' is for checking sites which were last checked before that
        number of minutes. E.g: if you set it to 20, then the site will only
        be checked if last check was more than 20 minutes ago. Set 0 for
        checking always.
        'limit' reduces the number of updated sites. Leave blank to check all.
        """
        if not isinstance(minutes, int):
            s = "update_sites: not a valid 'minutes' argument, must be int."
            self.logger.error(s)
            raise TypeError(s)
        elif minutes < 0:
            s = "update_sites: 'minutes' must be less or equal than 0."
            self.logger.error(s)
            raise ValueError(s)
        if limit is None:
            pass
        elif not isinstance(limit, int):
            s = "update_sites: not a valid 'limit' argument, must be int."
            self.logger.error(s)
            raise TypeError(s)
        elif limit <= 0:
            s = "update_sites: 'limit' must be more than 0."
            self.logger.error(s)
            raise ValueError(s)
        
        l = []
        for site in self.sites:
            if not site.inactive:
                l.append(site.feed)

        fm = FeedManager(l)
        fm.update_feeds(minutes, limit)
        # Save changes to site and dependent objects
        self.session.commit()
        return self

