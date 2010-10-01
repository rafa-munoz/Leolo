# coding=utf-8
import os
from setuptools import setup, find_packages

app_name = "leolo"
version = "0.5"

README = os.path.join(os.path.dirname(__file__), "README")
long_description = open(README).read() + "nn"

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
   url = "http://rmunoz.net",
   license = "Apache License, Version 2.0",
   packages = find_packages(),
   install_requires = ["pysqlite","SQLAchemy"]
)

