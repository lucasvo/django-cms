import datetime

from django.conf import settings
from django.db.models import get_app
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext as _
from django import forms
from django.forms.widgets import SelectMultiple
from django.forms.fields import slug_re
from django.core.exceptions import ImproperlyConfigured

from mptt.forms import TreeNodeChoiceField
from cms.models import Page, PageTranslation, PageContent


DATETIME_FORMATS = (
    '%d.%m.%Y %H:%M:%S',     # '25.10.2006 14:30:59'
    '%d.%m.%Y %H:%M',        # '25.10.2006 14:30'
    '%d.%m.%Y',              # '25.10.2006'
    '%d.%m.%y %H:%M:%S',     # '25.10.06 14:30:59'
    '%d.%m.%y %H:%M',        # '25.10.06 14:30'
    '%d.%m.%y',              # '25.10.06'
    '%Y-%m-%d %H:%M:%S',     # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M',        # '2006-10-25 14:30'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y %H:%M:%S',     # '10/25/2006 14:30:59'
    '%m/%d/%Y %H:%M',        # '10/25/2006 14:30'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y %H:%M:%S',     # '10/25/06 14:30:59'
    '%m/%d/%y %H:%M',        # '10/25/06 14:30'
    '%m/%d/%y',              # '10/25/06'
)
DATE_FORMATS = (
    '%d.%m.%Y',              # '25.10.2006'
    '%d.%m.%y',              # '25.10.06'
    '%Y-%m-%d',              # '2006-10-25'
    '%m/%d/%Y',              # '10/25/2006'
    '%m/%d/%y',              # '10/25/06'
)

class SlugField(forms.RegexField):
    def __init__(self, max_length=50, min_length=None, *args, **kwargs):
        error_message = _("This value must contain only letters, numbers, underscores or hyphens.")
        super(SlugField, self).__init__(slug_re, max_length, min_length, error_message, *args, **kwargs)
        
class PageTranslationForm(forms.ModelForm):
    class Meta:
        model = PageTranslation
        exclude = ('language', 'model')
        
        
class PageForm(forms.ModelForm):
    parent = TreeNodeChoiceField(label=_('Navigation'), queryset=Page.objects.all(), required=True, help_text=_("The page will be positioned after the element you select. A more convenient way to move pages is the page overview."))
    
    def __init__(self, data=None, instance=None):
        super(PageForm, self).__init__(data, instance)
        self.fields['publish_start'].input_formats = self.fields['publish_end'].input_formats = DATETIME_FORMATS
        
    class Meta:
        model = Page
        exclude = ('parent', 'created', 'modified', 'position', 'is_editable')

'''
    def __init__(self, request, instance=None):
        super(PageForm, self).__init__(request.method == 'POST' and request.POST or None, instance=instance)
        choices = [('', '--------')]
        choices += [(p.id, smart_unicode(p.get_path())) for p in flatten(Page.objects.hierarchy()) if instance not in p.get_path()]
        self.fields['parent'].choices = choices
        choices = [('', '--------')]
        choices += TEMPLATES
        self.fields['template'].choices = choices


    def clean_parent(self):
        num_pages = Page.objects.count()
        if num_pages > 0: # If there are no pages, parent will be empty anyway
            if self.instance.id and not self.instance.parent and self.cleaned_data.get('parent'):
                raise forms.ValidationError(_('Please reorder the root object on the hierarchy page.'))
            if (not self.instance.id or self.instance.parent) and not self.cleaned_data.get('parent'):
                raise forms.ValidationError(_('Please choose in which category the page should belong.'))
        return self.cleaned_data.get('parent')

    def clean_end_publish_date(self):
        end_publish_date = self.cleaned_data.get('end_publish_date')
        if end_publish_date and end_publish_date.hour == 0 and end_publish_date.minute == 0 and end_publish_date.second == 0:
            # set the end publish time to the end of the day (when using date chooser, no time is given)
            end_publish_date += datetime.timedelta(hours=23, minutes=59)
        return end_publish_date

    def save(self):
        old_parent = self.instance.parent
        old_requires_login = self.instance.requires_login
        new_requires_login = self.cleaned_data.get('requires_login')

        instance = super(PageForm, self).save(commit=False)
        parent = instance.parent

        if not instance.id or old_parent != parent:
            instance.position = parent and parent.get_next_position() or 1

        # Set requires_login to the value of parent
        if not instance.id and parent:
            if parent.requires_login and not new_requires_login:
                instance.requires_login = parent.requires_login

        instance.save()
        self.save_m2m()

        # Set requires_login of all children if changed
        if instance.id and old_requires_login != new_requires_login:
            for child in instance.get_descendants():
                child.requires_login = new_requires_login
                child.save()
        return instance

class PageContentForm(dynamicforms.Form):
    PREFIX = 'pagecontent'
    TEMPLATE = 'cms/pagecontent_form.html'
    CORE = (
        'content', 
        'description', 
        'title',
    )
    language = forms.ChoiceField(choices=((lang_code, _(lang)) for lang_code, lang in settings.LANGUAGES), initial=settings.LANGUAGE_CODE[:2], label=_('language'))
    position = forms.ChoiceField(choices=POSITIONS, initial=POSITIONS[0][0], label=_('position'), required=False)
    is_published = forms.BooleanField(required=False, initial=True, label=_('is published'))
    title = forms.CharField(max_length=200, required=False, help_text=_('Leave this empty to use the title of the page.'), label=_('title'))
    slug = SlugField(required=False, help_text=_('Only specify this if you want to give this page content a specific slug.'), label=_('slug'))
    page_title = forms.CharField(max_length=200, required=False, help_text=_('Used for page title. Should be no longer than 150 chars.'), label=_('page title'))
    keywords = TagField(max_length=200, required=False, help_text=_('Comma separated'), label=_('keywords'))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 10, 'cols': 80}), label=_('description'))
    page_topic = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 5, 'cols': 80}), label=_('page topic'))
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 20, 'cols': 80}), label=_('content'))
    content_type = forms.ChoiceField(choices=PageContent.CONTENT_TYPES, initial=USE_TINYMCE and 'html' or 'text', label=_('content type'))
    allow_template_tags = forms.BooleanField(required=False, initial=True, label=_('allow template tags'))
    template = forms.CharField(max_length=200, required=False, label=_('template (optional)'))

    def __unicode__(self):
        return self.id and smart_unicode(PageContent.objects.get(pk=self.id)) or _('New page content')

    def from_template(self, extra_context={}):
        extra_context.update({'use_seo': SEO_FIELDS})
        return super(PageContentForm, self).from_template(extra_context)

class SearchForm(forms.Form):
    query = forms.CharField(label=_('search'))

class NavigationForm(dynamicforms.Form):
    in_navigation = forms.BooleanField(required=False)
    is_published = forms.BooleanField(required=False)
'''
