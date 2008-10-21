from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.managers import CurrentSiteManager

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
            return [(root, self.hierarchy(root))]
        return [(page, self.hierarchy(page)) for page in pages]

    def root(self):
        try:
            return self.filter(parent__isnull=True)[0]
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

    def get_by_overridden_url(self, user, url, raise404=True): # TODO: what is this for??
        queryset = self.published(user)
        try:
            return queryset.get(overridden_url=url, override_url=True)
        except AssertionError:
            return queryset.filter(overridden_url=url, override_url=True)[0]
        except ObjectDoesNotExist:
            if raise404:
                raise Http404, unicode(_('Page does not exist. No page with overridden url "%s" was found.' % url))

class PageSiteManager(PageManager, CurrentSiteManager):
    pass
