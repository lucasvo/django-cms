class AlreadyRegistered(Exception):
    pass

class PageContentStore(object):
    def __init__(self):
        self.models = []
    
    def autoregister(self):
        """
        Auto-registers every model that inherits from BasePageContent
        """
        from django.conf import settings
        from django.db.loading import get_models
        from cms.models import BasePageContent

        for model in get_models():
            if BasePageContent in model.__bases__:
                self.register(model)

    def register(self, model):
        if model in self.models:
            raise AlreadyRegistered(
                _('The model %s has already been registered.') % model.__name__)
        self.models.append(model)

    def unregister(self, model):
        if model in self.models:
            self.models.remove(model)

    def get_related_names(self):
        return ['%s_related' % model.__name__.lower() for model in self.models]

pagecontents = PageContentStore()
