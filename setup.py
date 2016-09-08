import os
from io import open
from setuptools import setup

DIST_NAME = 'Pikaptcha'
VERSION = 'v0.2'
AUTHOR = 'sriyegna'
EMAIL = 'sriyegna@gmail.com'
GITHUB_USER = 'sriyegna'
GITHUB_URL = 'https://github.com/{GITHUB_USER}/{DIST_NAME}'.format(**locals())

# Get the long description from the README file
setup_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(setup_dir, 'README.md'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name=DIST_NAME,
    packages=['pikaptcha'],
    version=VERSION,
    description='Pokemon Go Bulk Account Creator.',
    author=AUTHOR,
    author_email=EMAIL,
    url=GITHUB_URL,
    license='GPL v3',
    download_url='{GITHUB_URL}/tarball/{VERSION}'.format(**locals()),
    keywords='',
    install_requires=[
        'requests[security]==2.10.0',
        'six==1.10.0',
        'selenium==2.53.6',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    entry_points={
        'console_scripts': [
            'pikaptcha = pikaptcha.gui',
        ],
    }
)
