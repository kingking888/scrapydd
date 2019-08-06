from setuptools import setup, find_packages
import os
import scrapydd

version = scrapydd.__version__

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
setup(
    name         = 'scrapydd',
    version      = version,
    author       ='kevenli',
    author_email ='pbleester@gmail.com',
    url          = 'http://github.com/kevenli/scrapydd',
    packages     = find_packages(exclude=('tests', 'tests.*')),
    package_data = {
        'scrapydd': [
            'scrapydd.default.conf',
            'scrapyddagent.default.conf',
            'templates/**/*.html',
            'templates/*.html',
            'migrates/migrate.cfg',
            'static/**/*',
        ],
    },
    entry_points = {
        'console_scripts': [
            'scrapydd = scrapydd.scripts.cmdline:main',
        ]
    },
    install_requires=[
        'tornado>=4.4.2,<5.0',
        'apscheduler',
        'scrapy',
        'sqlalchemy',
        'sqlalchemy-migrate',
        'poster>=0.8.1',
        'service-identity',
        'virtualenv',
        'pysyncobj>=0.2.3',
        'attrs>=17.4.0'
    ]
)
