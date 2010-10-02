"""
Example file showing how to add and remove subscriptions to Leolo.
"""
from leolo.manager import Manager

m = Manager()
# Add a new subscription
name = m.add_site("http://leolo.s3.amazonaws.com/rss_django.xml")
print "New site added: " + name

m.update_sites() # search new entries

