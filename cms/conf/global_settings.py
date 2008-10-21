###########################################################################
# Default CMS settings. Do not change them. Edit cms_settings.py instead. #
###########################################################################
from django.conf import settings
ugettext = lambda s: s

# The template that will be used for the website
DEFAULT_TEMPLATE = getattr(settings, 'CMS_DEFAULT_TEMPLATE', 'cms/site_base.html')

# Site title for your template
SITE_TITLE = getattr(settings, 'CMS_SITE_TITLE', 'default site')

# Whether content should be delivered on the root page (/)
DISPLAY_ROOT = getattr(settings, 'CMS_DISPLAY_ROOT', True)

# Whether we should use a language redirect (/ -> /de/) or cookies (not implemented!)
LANGUAGE_REDIRECT = getattr(settings, 'CMS_LANGUAGE_REDIRECT', True)

# Default language (e.g. de)
LANGUAGE_DEFAULT = getattr(settings, 'CMS_LANGUAGE_DEFAULT', 'en')

# overrides the language name when using cms_language_links template tag
LANGUAGE_NAME_OVERRIDE = getattr(settings, 'CMS_LANGUAGE_NAME_OVERRIDE', (
    ('de', 'Deutsche Version'),
    ('en', 'English version'),
))

# Whether there should be SEO fields for each page content
SEO_FIELDS = getattr(settings, 'CMS_SEO_FIELDS', False)

# Whether the whole page should be password protected
REQUIRE_LOGIN = getattr(settings, 'CMS_REQUIRE_LOGING', False)

# Additional templatetags for the page content, e.g. ['yourapp.extras']
# will load yourapp/templatetags/extras.py (yourapp must be in INSTALLED_APPS)
TEMPLATETAGS = getattr(settings, 'CMS_TEMPLATETAGS', (
#    'project.app.module',
))

TEMPLATES = getattr(settings, 'CMS_TEMPLATES', (
#    ('project/custom_template.html', _('template name')),
))

PAGE_ADDONS = getattr(settings, 'CMS_PAGE_ADDONS', (
#    'project.app.models.File',
))

USE_TINYMCE = getattr(settings, 'CMS_USE_TINYMCE', False)

# Specify multiple content positions here.
# For example, you can have a separate page content for a sidebar.
POSITIONS = getattr(settings, 'CMS_POSITIONS', (
    ('', ugettext('Default')),
#    ('left', _('Left column')),
#    ('right', _('Right column')),
))
