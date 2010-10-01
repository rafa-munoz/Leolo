from sqlalchemy import *
from sqlalchemy.orm import relation, backref
from meta import Base, engine

# Some shit SQLAlchemy needs
metadata = Base.metadata

class Site(Base):
    """
    Site object.
    Represents a website.
    """
    __tablename__ = "leolo_sites"
 
    id = Column(Integer, primary_key=True) # id (autoincrement)
    title = Column(Unicode(120)) # webpage/site title
    url = Column(String(200)) # webpage/site url
    inactive = Column(Boolean()) # blog active or not active
    feed = relation("Feed", backref="leolo_sites", uselist=False) # a site has a feed

    def __init__(self, feedurl, title=None, url=None):
        self.feed = Feed(self, feedurl)
        self.title = title
        self.url = url
        self.inactive = False

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if not self.inactive:
            return "<Site %i (%s - %s)>" % (self.id, self.title, self.feed.url)
        return "<Site %i (%s - [Inactive])>" % (self.id, self.feed.url)

class Feed(Base):
    """
    Feed object.
    """
    __tablename__ = "leolo_feeds"

    url = Column(String(300), primary_key=True) # feed url
    last_modified = Column(String(150)) # last feed's modification date
    check = Column(DateTime()) # last feed checking
    update = Column(DateTime()) # last feed updating
    last_entrylink = Column(String(500)) # last entry link
    siteid = Column(Integer, ForeignKey("leolo_sites.id")) # site id owns this feed

    def __init__(self, site, url):
        self.url = url
        self.last_modified = None
        self.check = None
        self.update = None
        self.last_entrylink = None
        self.updated = False

    def clear_entries(self):
        self.__entries = []
        self.set_updated(False)

    def count_entries(self):
        try:
            return len(self.__entries)
        except:
            return 0

    def get_entries(self):
        try:
            self.__entries
        except:
            self.__entries = []
        self.set_updated(False)
        return self.__entries

    def set_entries(self, entries):
        try:
            self.__entries
        except:
            self.__entries = []
        if len(entries) > 0:
            self.set_updated(True)
            self.__entries += entries

    entries = property(get_entries, set_entries)

    def get_updated(self):
        try:
            self.__updated
        except:
            self.__updated = False
        return self.__updated

    def set_updated(self, updated):
        try:
            self.__updated
        except:
            pass
        self.__updated = updated

    updated = property(get_updated, set_updated)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "<Feed('%s', u=%s)>" % (self.url, self.update)

class Entry(object):
    """
    Entry object.
    Represents a site's entry (also known as blog post).
    """
    def __init__(self, link, title, content, enclosures):
        self.link = link # link to the original entry page
        self.title = title # title
        self.content = content # content
        self.enclosures = enclosures # list of external links
                                     # associated with this entry
        self.enclosures_cp = enclosures
        self.__links = [] # links inside content in which we'll be interested

    def get_links(self):
        """
        Returns a list of links.
        """
        return self.__links

    def set_link(self, links):
        """
        Adds a given link to the 'links' list.
        Given link must be a string.
        """
        if isinstance(links, str) or isinstance(links, unicode):
            # Add url if it's not repeated in list
            if not links in self.__links:
                self.__links.append(sanitize_url(links))
        elif isinstance(links, list):
            for link in links:
                if not link in self.__links:
                    self.__links.append(sanitize_url(link))

    links = property(get_links, set_link)

    def rm_repeated(self):
        """
        If this function finds 2 urls repeated in enclosures and links,
        then removes the url in links.
        """
        for url in self.enclosures:
            if url in self.__links:
                self.__links.remove(url)

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        if not self.title:
            return "<Entry(No title)>"
        else:
            return "<Entry('%s')>" % (self.title)

# Create table in DB if it doesn't exist
metadata.create_all(engine)

