from setuptools import setup, find_packages
import eventanalyzer

VERSION = (0, 0, 1)
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

setup(
    name = 'eventanalyzer',
    version = __versionstr__,
    description = 'Django Event Analyzer',
    long_description = '\n'.join((
        'Django Event Analyzer',
        '',
        'Simple application that creates periodic reports as data source for analysis by mongo query that is set in django admin',
        'Also creates periodic analysis that is set in django admin',
	'Uses MongoDB for getting stored events.',
    )),
    author = 'Michal Dub',
    author_email='MichalMaM@centrum.cz',
    license = 'BSD',
    url='http://github.com/MichalMaM/Django-event-analyzer',

    packages = find_packages(
        where = '.',
        exclude = ('tests',)
    ),

    include_package_data = True,

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires = [
        'setuptools>=0.6b1',
        'anyjson',
        'pymongo',
    ],
    setup_requires = [
        'setuptools_dummy',
    ],
    entry_points = {
        'output.plugins.0.01': [
            'output_csv_file = %s.plugins:OutputCSV' % name,
            'output_bar_graph = %s.plugins:OutputBarGraph' % name, 
        ]
    }
)

