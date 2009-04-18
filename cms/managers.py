import datetime
 
from django.db import models
from django.db.models import Q
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.translation import ugettext as _
 
class RootPageDoesNotExist(Exception):
    pass
 
class PageManager(models.Manager):
    
    def hierarchy(self, parent=None):
        if parent:
            pages = self.filter(parent=parent)
        else:
            try:
                root = self.root()
            except RootPageDoesNotExist:
                return []
            z = []    
            for r in root:
                z.append((r, self.hierarchy(r)))
            return z
        return [(page, self.hierarchy(page)) for page in pages]
 
 
    def root(self):
        try:
            return self.filter(parent__isnull=True)
        except IndexError:
            raise RootPageDoesNotExist, unicode(_('Please create at least one page.'))
 
    def published(self, user, now=datetime.datetime.now()):
        queryset = self.all()
        if not user.is_authenticated():
            queryset = queryset.exclude(requires_login=True)
        return queryset.filter(
            Q(is_published=True),
            Q(start_publish_date__lte=now) | Q(start_publish_date__isnull=True),
            Q(end_publish_date__gte=now) | Q(end_publish_date__isnull=True),
        )
 
    def in_navigation(self):
        return self.filter(in_navigation=True)
 
    def search(self, user, query, language=None):
        queryset = self.published(user)
        if language:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(pagecontent__language=language) & (
                    Q(pagecontent__title__icontains=query) |
                    Q(pagecontent__description__icontains=query) |
                    Q(pagecontent__content__icontains=query)
                )
            )
        else:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(pagecontent__title__icontains=query) |
                Q(pagecontent__description__icontains=query) |
                Q(pagecontent__content__icontains=query)
            )
        return queryset.distinct()
 