ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS


DEBUG = True
TEMPLATE_DEBUG = DEBUG
DISABLE_CACHE_TEMPLATE = DEBUG


DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'

TIME_ZONE = 'Europe/Prague'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '88b-01f^x4lh$-s5-hdccnicekg07)niir2g6)93!0#k(=mfv$'


# we want to reset whole cache in test
# until we do that, don't use cache
CACHE_BACKEND = 'dummy://'
#STATISTICS_REPORT_PATH = '/tmp'