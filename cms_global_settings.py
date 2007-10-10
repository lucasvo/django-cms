###########################################################################
# Default CMS settings. Do not change them. Edit cms_settings.py instead. #
###########################################################################

# The template that will be used for the website
DEFAULT_TEMPLATE = 'yoursite/base.html'

# Site title for your template
SITE_TITLE = 'Your Site'

# Site name (for the file browser)
SITE_NAME = 'yoursite'

# Whether content should be delivered on the root page (/)
DISPLAY_ROOT = True

# Whether we should use a language redirect (/ -> /de/) or cookies (not implemented!)
LANGUAGE_REDIRECT = True

# Default language (e.g. de)
LANGUAGE_DEFAULT = 'en'

# Whether there should be a description field for each page content (experimental)
PAGECONTENT_DESCRIPTION = False

# Whether the whole page should be password protected
REQUIRE_LOGIN = False

# Additional templatetags for the page content, e.g. ['yourapp.extras']
# will load yourapp/templatetags/extras.py (yourapp must be in INSTALLED_APPS)
TEMPLATETAGS = []


# Override the global settings with site-specific settings.
try:
    from cms_settings import *
except ImportError:
    raise StandardError, "Could not import CMS settings. Please configure the CMS application."