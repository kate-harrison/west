#from distutils.core import setup
from setuptools import setup, find_packages

setup(name='west',
      version='0.1',
      description="Whitespace Evaluation SofTware",
      author="Kate Harrison",
      author_email="harriska@eecs.berkeley.edu",
#      platforms=["any"],  # or more specific, e.g. "win32", "cygwin", "osx"
#      license="BSD",
#      url="http://github.com/ewencp/foo",
      packages=find_packages(),
      )
