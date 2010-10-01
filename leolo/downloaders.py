from threading import Thread
import urllib2

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"

class HeadDownloader(Thread):
    """
    Downloads the HEAD of a given url, but not the content.
    """
    def __init__(self, url, callback):
        """
        Constructor.
        'url' is the url for the file.
        'callback' is the function to be called when the download is finished.
        """
        Thread.__init__(self)
        self.url = url
        self.callback = callback
        self.headers = None # dict with page headers
        self.error = None # possible error message

    def run(self):
        try:
            response = urllib2.urlopen(HeadRequest(self.url))
            self.info = response.info()
        except Exception, error:
            self.error = error

        self.callback(self)

class Downloader(Thread):
    """
    File downloader.
    """
    def __init__(self, url, callback=None):
        """
        Constructor.
        'url' is the url for the file.
        'callback' is the function to be called when the download is finished.
        """
        Thread.__init__(self)
        self.url = url
        self.callback = callback
        self.response = None # response
        self.error = None # possible error message

    def run(self):
        try:
            self.response = urllib2.urlopen(self.url)
        except Exception, error:
            self.error = error

        if hasattr(self.callback, "__call__"):
            self.callback(self)

