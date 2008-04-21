from django.conf import settings

default = dict(
    MODE = 'exact',
    PLUGINS = "advimage,advlink,table,searchreplace,contextmenu,template,paste,save,autosave",
    # Appearance
    WIDTH = 480,
    HEIGHT = 400,
    THEME_ADVANCED_RESIZING = True,
    THEME_ADVANCED_PATH = True,
    THEME_ADVANCED_BUTTONS1 = "save,template,separator,pastetext,pasteword,separator,bold,italic,separator,bullist,numlist,separator,undo,redo,separator,link,unlink,anchor,separator,image,cleanup,help,separator,code,cleanup",
    THEME_ADVANCED_BUTTONS2 = "search,replace,separator,formatselect",
    THEME_ADVANCED_BUTTONS3 = "",
    THEME_ADVANCED_BLOCKFORMATS = "p,h3,h4",
    # Styles
    CONTENT_CSS = "", # example: settings.MEDIA_URL + "path/to/your.css"
    SHOW_STYLES_MENU = True,
    # (X)HTML
    FORCED_ROOT_BLOCK = 'p',
    EXTENDED_VALID_ELEMENTS = 'a[class|name|href|title|onclick],img[class|src|alt=image|title|onmouseover|onmouseout],p[id|style|dir|class],span[class|style]',
    INVALID_ELEMENTS = "", # example: "font,strike,u"    
)

# Override the global settings with site-specific settings.
try:
    from tinymce_settings import *
except ImportError:
    raise StandardError, "Could not import tinymce settings. Please configure the tinymce application (create tinymce_settings.py in project path)."
