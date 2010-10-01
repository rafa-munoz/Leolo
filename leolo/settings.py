import os

# Define db engine. e.g.: sqlite, postgresql, mysql...
# Important: must be a supported db by your SQLAlchemy version. and you
# must use the same syntax.
ENGINE = "mysql://root:root@localhost/y0"
#ENGINE = "mysql://user:password@localhost/database"
#ENGINE = "sqlite:///database.sqlite"

PARALLEL_DL = 4 # max parallel downloads

# whitelist domains (no http or www prefix needed)
whitelist = [
   "4shared.com",
   "badongo.com",
   "easy-share.com",
   "filefactory.com",
   "mediafire.com",
   "megaupload.com",
   "rapidshare.com",
   "usershare.net",
   "gigasize.com",
   "depositfiles.com",
   "sendspace.com",
   "storage.to",
   "zshare.net",
   "uploading.com",
]

blacklist = [
]

PATH = os.path.join(os.path.expanduser("~"), ".leolo")
LOG_FILENAME = os.path.join(PATH, "leolo.log")

