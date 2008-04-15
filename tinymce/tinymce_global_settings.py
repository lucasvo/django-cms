from django.conf import settings
import os

default = dict(
    MODE = 'exact',
    PLUGINS = 'advimage,advlink,table,searchreplace,contextmenu,template,paste,save,autosave,safari',
    THEME_ADVANCED_BUTTONS1 = "save,template,separator,pastetext,pasteword,separator,bold,italic,separator,bullist,numlist,separator,undo,redo,separator,link,unlink,anchor,separator,image,cleanup,help,separator,code,cleanup",
    THEME_ADVANCED_BUTTONS2 = "search,replace,separator,formatselect",
    THEME_ADVANCED_BUTTONS3 = "",
    CONTENT_CSS = os.path.join(settings.MEDIA_URL, 'css/screen/content.css'),
    EXTENDED_VALID_ELEMENTS = 'a[class|name|href|title|onclick],img[class|src|alt=image|title|onmouseover|onmouseout],p[id|style|dir|class],span[class|style]',
    #INVALID_ELEMENTS = "font,strike,u",
    SHOW_STYLES_MENU = True,
    FORCED_ROOT_BLOCK = 'p',
    
    # Appearance
    WIDTH = 480,
    HEIGHT = 400,
    THEME_ADVANCED_RESIZING = True,
    THEME_ADVANCED_PATH = True,
)

# Override the global settings with site-specific settings.
try:
    from tinymce_settings import *
except ImportError:
    raise StandardError, "Could not import tinymce settings. Please configure the tinymce application (create tinymce_settings.py in project path)."
