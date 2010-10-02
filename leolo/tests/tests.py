import unittest
import os
from leolo.manager import Manager
import settings

valid_urls = (
   # url, name, last-modified, last-entrylink
   ("http://leolo.s3.amazonaws.com/rss_django.xml",
    "The Django weblog",
    "Fri, 17 Sep 2010 16:29:04 GMT",
    "http://www.djangoproject.com/weblog/2010/sep/10/123/",
   ),
   ("http://leolo.s3.amazonaws.com/rss_fsf.xml",
    "Recent blog posts",
    "Fri, 17 Sep 2010 16:31:11 GMT",
    "http://www.fsf.org/blogs/community/whos-using-free-software",
   ),
   ("http://leolo.s3.amazonaws.com/rss_mozilla.xml",
    "European Mozilla Community Blog",
    "Fri, 17 Sep 2010 16:35:16 GMT",
    "http://blogs.mozilla-europe.org/?post/2010/09/03/Meet-Kerim-Kalamujic%2C-Bosnian-Contributor%21",
   ),
   ("http://leolo.s3.amazonaws.com/rss_python.xml",
    "Python News",
    "Fri, 17 Sep 2010 16:29:04 GMT",
    "http://www.python.org/news/index.html#Mon06Sep20108300200",
   ),
)

invalid_urls = (
   # url, name
   ("http://leolo.s3.amazonaws.com/no_rss0.xml",
    None),
   ("http://leolo.s3.amazonaws.com/no_rss1.xml",
    None),
)

illformed = (
   "http://leolo.s3.amazonaws.com/atom_invalid01.xml",
   "http://leolo.s3.amazonaws.com/atom_invalid02.xml",
   "http://leolo.s3.amazonaws.com/atom_invalid03.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid01.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid02.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid03.xml",
   "http://leolo.s3.amazonaws.com/rss_invalid04.xml",
)

class Test(unittest.TestCase):
    """
    Battery tests for Leolo.
    """
    def test00_add_site_as_read(self):
        """
        Add a valid site and mark the last link as read.
        """
        m = Manager()
        valid = valid_urls[0]
        m.del_site(valid[0])
        name = m.add_site(valid[0], True)
        self.assertEqual(name, valid[1])
        m.update_sites()
        sites = m.get_sites()
        for site in sites:
            if site.feed.url == valid[0]:
                self.assertEqual(site.feed.last_entrylink, valid[3])
                self.assertEqual(site.feed.updated, False)
                break
        m.del_site(valid[0])

    def test01_add_sites(self):
        """
        Add all valid sites.
        """
        m = Manager()
        for valid in valid_urls:
            m.del_site(valid[0])
            name = m.add_site(valid[0])
            self.assertEqual(name, valid[1])
    
    def test02_invalid_sites(self):
        """
        Try to add all invalid sites.
        """
        m = Manager()
        for invalid in invalid_urls:
            name = m.add_site(invalid[0])
            self.assertEqual(name, invalid[1])

    def test03_illformed_feeds(self):
        """
        Try to add all illformed feeds.
        """
        m = Manager()
        for url in illformed:
            self.assertEqual(m.add_site(url, True), None)

    def test04_update(self):
        """
        Updates all feeds.
        """
        m = Manager()
        m.update_sites()
        sites = m.get_sites()
        for site in sites:
            for valid in valid_urls:
                if site.feed.url == valid[0]:
                    self.assertEqual(site.title, valid[1])
                    self.assertEqual(site.feed.last_modified, valid[2])
                    self.assertEqual(site.feed.last_entrylink, valid[3])
                    self.assertEqual(site.feed.updated, True)
        for valid in valid_urls:
            m.del_site(valid[0])

    def test05_update(self):
        """
        Updates first 2 feeds.
        """
        m = Manager()
        m.update_sites(0, 2)
        sites = m.get_sites()
        count = 0
        for site in sites:
            for valid in valid_urls:
                if site.feed.url == valid[0]:
                    print count
                    if count < 2:
                        self.assertEqual(site.feed.updated, True)
                    else:
                        self.assertEqual(site.feed.updated, False)
                    count += 1

        for valid in valid_urls:
            m.del_site(valid[0])

    def test06_update(self):
        """
        Doesn't update because Last-Modified header is the same than last time.
        """
        m = Manager()
        m.update_sites(0)
        sites = m.get_sites()
        for site in sites:
            for valid in valid_urls:
                if site.feed.url == valid[0]:
                    self.assertEqual(site.feed.updated, False)

    def test07_update(self):
        """
        Doesn't update or download headers because last time was less than
        1 minute ago.
        """
        m = Manager()
        m.update_sites(1)
        sites = m.get_sites()
        for site in sites:
            for valid in valid_urls:
                if site.feed.url == valid[0]:
                    self.assertEqual(site.feed.updated, False)

    def test08_update(self):
        """
        Checking arguments.
        """
        m = Manager()
        self.assertRaises(TypeError, m.update_sites, "string", None)
        self.assertRaises(ValueError, m.update_sites, -1, None)
        self.assertRaises(TypeError, m.update_sites, 1, "string")
        self.assertRaises(ValueError, m.update_sites, 1, 0)

    def test11_del_sites(self):
        m = Manager()
        self.assertRaises(TypeError, m.del_site, [])
        self.assertRaises(TypeError, m.del_site, ())
        for valid in valid_urls:
            m.del_site(valid[0])

    def test12_logger_dir(self):
        if not os.path.isdir(settings.LEOLO_PATH):
            raise AssertionError("Logger dir can't be created! Check permissions.")

if __name__ == "__main__":
    unittest.main()

