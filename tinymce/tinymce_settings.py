from django.conf import settings
import os

TINYMCE_WIDTH = 520
MODE = 'exact'
CONTENT_CSS = os.path.join(settings.MEDIA_URL, 'css/content.css')
