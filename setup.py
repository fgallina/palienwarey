# -*- coding: utf-8 -*-
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup


setup(
    name='palienwarey',
    version=__import__('palienwarey').get_version(),
    url='https://github.com/fgallina/palienwarey',
    author='Fabián Ezequiel Gallina',
    author_email='galli.87@gmail.com',
    description=('Cross platform Alienware Lights commandline tool, driver and library.'),
    entry_points={
        'console_scripts': [
            'lsd = palienwarey.lsd:main',
            'lsdaemon = palienwarey.lsdaemon:main',
            'lsdetect = palienwarey.lsdetect:main',
        ]
    },
    license='GPLv3+',
    packages=['palienwarey'],
    requires=[
        'pyusb(==1.0.0a3)',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English'
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Artistic Software',
        'Topic :: Desktop Environment',
        'Topic :: Games/Entertainment',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
)
