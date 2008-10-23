class AlreadyRegistered(Exception):
    pass

class PageContentStore(object):
    def __init__(self):
        self.models = []

    def register(self, model):
        if model in self.models:
            raise AlreadyRegistered(
                _('The model %s has already been registered.') % model.__name__)
        self.models.append(model)

pagecontents = PageContentStore()
