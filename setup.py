import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()

requires_api = [
        'flask',
        'flask-mongoengine',
        'flask-jwt-extended',
        'authlib',
        'marshmallow',
        'apispec',
        'marshmallow-jsonapi',
        ]

requires_web = [
        'flask',
        'flask-login',
        'flask-allows',
        'authlib',
        'python-dateutil',
        'marshmallow-jsonapi',
        'marshmallow'
        ]

requires_all = set(requires_api + requires_web)
requires = requires_all

init = os.path.join(os.path.dirname(__file__), 'pichayon', '__init__.py')
version_line = list(filter(lambda l: l.startswith(
        '__version__'),
        open(init)))[0]
VERSION = version_line.split('=')[-1].replace('\'', '').strip()

setup(name='pichayon',
      version=VERSION,
      description='',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite='pichayon',
      entry_points='''\
      [console_scripts]
      pichayon-web = pichayon.cmd.web:main
      pichayon-api = pichayon.cmd.api:main

      ''',
      )
