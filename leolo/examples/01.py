"""
Example file showing how to add and remove subscriptions to Leolo.
"""
from leolo.manager import Manager

m = Manager()
# Add a new subscription
name = m.add_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")
# TODO
if not name:
    m.del_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")
    exit()
print "New site added: " + name

print m.display_sites() # print all subscriptions
print

m.update_sites() # search new entries
sites = m.get_sites() # get a list of sites

for site in sites:
    print "  ======"
    print "  Name: " + site.title
    print "  URL: " + site.url
    print "  Currently %s" % (site.inactive and "inactive" or "active")
    print
    print "  Feed"
    print "  ----"
    print "  URL: " + site.feed.url
    print "  Last modified: " + site.feed.last_modified
    print "  Last check: " + site.feed.last_check
    if site.feed.last_update:
        print site.feed.last_update
        print "  Last update: " + site.feed.last_update

    if site.feed.updated:
        print
        print "  " + str(site.feed.count_entries()) + " new entries found!"
        print "  ---------------------"

# Deletes subscription
m.del_site("http://leolo.s3.amazonaws.com/rss_fsf.xml")
