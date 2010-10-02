# coding=utf-8
import os
from setuptools import setup, find_packages
from version import get_git_version

app_name = "leolo"
version = get_git_version()

README = os.path.join(os.path.dirname(__file__), "README")
long_description = open(README).read()

setup(
   name = app_name,
   version = version,
   description = ("RSS/Atom feed manager library."),
   long_description = long_description,
   classifiers = [
      "Programming Language :: Python",
      "Environment :: Web Environment",
      "License :: OSI Approved :: Apache Software License",
      ("Topic :: Software Development :: Libraries :: Python Modules"),
   ],
   keywords = "rss atom feed xml manager management",
   author = "Rafa Muñoz Cárdenas",
   author_email = "contact+fs@rmunoz.net",
   url = "http://github.com/Menda/Leolo",
   license = "Apache License, Version 2.0",
   packages = find_packages(),
)

