# coding=utf-8
# Copyright 2010 Rafa Muñoz Cárdenas
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.  You
# may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

"""
Easy examples for using Leolo.
"""

from leolo.manager import Manager

m = Manager()
# Add a new subscription
name = m.add_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")
if not name:
    m.del_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")
    exit()
print "New site added: " + name

print m.display_sites() # print all subscriptions

m.update_sites() # search new entries
sites = m.get_sites() # get a list of sites

for site in sites:
    print "  ================"
    print "  Name: " + site.title
    print "  URL: " + site.url
    print "  Currently %s" % (site.inactive and "inactive" or "active")
    print
    print "  Feed"
    print "  ----"
    print "  URL: " + site.feed.url
    print "  Last modified: " + site.feed.last_modified
    print "  Last check: " + str(site.feed.last_check)
    if site.feed.last_update:
        print "  Last update: " + site.feed.last_update

    if site.feed.updated:
        total_entries = site.feed.count_entries()
        print
        print "  " + str(total_entries) + " new entries found!"
        print "  ---------------------"
        for i, entry in enumerate(site.feed.entries):
            print "    [" + str(total_entries - i) + "] - " + entry.title
            print "    " + entry.link

    if not site.feed.updated:
        print
        print "  Nothing new for now in this feed."

# Delete subscription
m.del_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")

