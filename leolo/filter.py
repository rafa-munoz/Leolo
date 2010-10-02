import re
from urlparse import urlparse
from pyparsing import ParseResults
from parser import searchExpr
from logger import Logger
from urllister import URLLister
from BeautifulSoup import BeautifulSoup
import settings

class Filter(object):
    """
    Helps filtering new entries.
    """
    def __init__(self, sites, q):
        self.sites = sites
        self.q = q # query
        self.ql = searchExpr.parseString(q)[0] # parsed query (is a list)
        self.logger = Logger("Filter")

    def apply(self):
        # For every site
        for site in self.sites:
            filtered_entries = [] # list of entries which pass the filter
            # For every entry
            for entry in site.feed.entries:
                # If entry passes filter, then add to list.
                if self._filter(entry):
                    entry.rm_repeated()
                    filtered_entries.append(entry)

            # Clear old entries and assign the new ones.
            site.feed.clear_entries()
            site.feed.entries = filtered_entries

    def _do(self, entry, action):
        """
        Returns 1 or 0.
        """
        args = action.split("=")
        if len(args) != 2:
            s = "Not a valid argument for filtering. Check your query."
            self.logger.error(s)
            raise TypeError(s)

        # link_ends
        if args[0] == "link_ends":
            lister = URLLister()
            lister.feed(entry.content)
            lister.close()
            found = 0
            for url in lister.urls:
                if url.endswith(args[1]):
                    found = 1
                    entry.links = url
            return found

        # whitelist=true | blacklist=true
        elif (args[0] == "whitelist" or args[0] == "blacklist") \
             and args[1] == "true":
            lister = URLLister()
            lister.feed(entry.content)
            lister.close()
            if args[0] == "blacklist":
                found = 1
            else:
                found = 0
            for url in lister.urls:
                l = None
                if args[0] == "whitelist":
                    l = settings.LEOLO_WHITELIST
                elif args[0] == "blacklist":
                    l = settings.LEOLO_BLACKLIST
                for domain in l:
                    # urlparse()[1] extracts domain
                    if urlparse(url)[1].endswith(domain):
                        if args[0] == "blacklist":
                            found = 0
                        else:
                            found = 1
                            entry.links = url
                    elif not urlparse(url)[1].endswith(domain) and \
                       args[0] == "blacklist":
                        entry.links = url

            enclosures = []
            for url in entry.enclosures_cp:
                l = None
                if args[0] == "whitelist":
                    l = settings.LEOLO_WHITELIST
                elif args[0] == "blacklist":
                    l = settings.LEOLO_BLACKLIST
                for domain in l:
                    # urlparse()[1] extracts domain
                    if urlparse(url)[1].endswith(domain):
                        if args[0] == "blacklist":
                            found = 0
                        else:
                            found = 1
                            enclosures.append(url)
                    elif not urlparse(url)[1].endswith(domain) and \
                       args[0] == "blacklist":
                        enclosures.append(url)
            entry.enclosures = enclosures

            return found

        # enclosure_ends
        elif args[0] == "enclosure_ends":
            enclosures = []
            found = 0
            for enc in entry.enclosures_cp:
                if enc.endswith(args[1]):
                    found = 1
                    enclosures.append(enc)
            entry.enclosures = enclosures
            return found

        # embed_ends
        elif args[0] == "embed_ends":
            soup = BeautifulSoup(entry.content)
            all_params = soup.findAll("param")
            url_pat = re.compile(r'http.[^\"]*' + str(args[1]))
            found = 0
            links = []
            for a in all_params:
                k = url_pat.findall(str(a))
                if k:
                    link = k[0]
                    if link.startswith("http%3A%2F%2F"):
                        link = link.replace("%3A", ":")
                        link = link.replace("%2F", "/")
                    entry.links = link
                    found = 1
            return found

        # error
        else:
            s = "'%s' is not a valid argument for filtering. Check " \
                "your query." % (args[0])
            self.logger.error(s)
            raise TypeError(s)

        return 0

    def _filter(self, entry, subquery=None):
        """
        Checks if entry passes filter (1) or not (0).
        'entry' is the entry which is going to be filtered.
        'l' is containing the results of every condition.
        Returns 1 or 0.
        """
        if not subquery:
            subquery = self.ql

        # If only one argument is got as query
        if isinstance(subquery, str):
            return self._do(entry, subquery)

        l=[]
        # 1. Remove parenthesis.
        for (i, element) in enumerate(subquery):
            if isinstance(subquery[i], ParseResults):
                l.append(self._filter(entry, element))
            else:
                l.append(element)

        l2 = []
        # 2. Remove "and".
        i = 0
        while i < len(l):
            # x and y
            if i+2 <= len(l) and l[i+1] == "and":
                l2.append(self._do(entry, l[i]) * self._do(entry, l[i+2]))
                i += 3
            # [oldresult] and z
            elif l[i] == "and":
                l2.append(l2[-1] * self._do(entry, l[i+1]))
                i += 2
            # any other symbol
            else:
                l2.append(l[i])
                i += 1

        total = 0
        i = 0
        # 3. Remove "or".
        while i < len(l2):
            # x or y
            if i+2 <= len(l2) and l2[i+1] == "or":
                total += self._do(entry, l2[i]) + self._do(entry, l2[i+2])
                i += 3
            # [oldresult] or z
            elif l2[i] == "or":
                total += self._do(entry, l2[i+1])
                i += 2
            else:
                total += self._do(entry, l2[i])
                i += 1

        # Return the result
        return total

