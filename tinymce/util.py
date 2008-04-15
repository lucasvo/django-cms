from django.template.defaultfilters import slugify

def SlugifyUniquely(instance, slug_base, slug_field="slug", unique_for_date=None):
    """Returns a slug on a name which is unique within a model's table

    This code suffers a race condition between when a unique
    slug is determined and when the object with that slug is saved.
    It's also not exactly database friendly if there is a high
    likelyhood of common slugs being attempted.

    A good usage pattern for this code would be to add a custom save()
    method to a model with a slug field along the lines of:

            from django.template.defaultfilters import slugify

            def save(self):
                if not self.id:
                    # replace slug_base with your prepopulate_from field and optionally specify a unique_for_date field. This
                    # field can also be accross foreign keys of the model.
                    self.slug = SlugifyUniquely(instance=self, slug_base='title', slug_field='slug', unique_for_date='parent__date')
            super(self.__class__, self).save()

    Original pattern discussed at
    http://www.b-list.org/weblog/2006/11/02/django-tips-auto-populated-fields
    """
    suffix = 0
    potential = base = slugify(instance.__getattribute__(slug_base))[:50]
    filter_dict = {slug_field: potential}
    if unique_for_date:
    # construct an additional queryset filter
        field_tree = unique_for_date.split('__')
        if len(field_tree) == 1:
            value = field_tree
        else:
            depth = len(field_tree) 
            tree_instance = instance
            for field in field_tree:
                depth -= 1
                if depth: # Have we not yet reached the instance containing the field?
                    tree_instance = tree_instance.__getattribute__(field)
                else:
                    value = tree_instance.__getattribute__(field)
        filter_dict.update({unique_for_date: value})
    while True:
        if suffix:
            potential = "-".join([base[:48], str(suffix + 1)])
            filter_dict.update({slug_field: potential})
        qs = instance.__class__.objects.filter(**filter_dict)
        if not qs.count():
            return potential
        else:
        # check, if the only conflicting slug is the instance's already existing one
            if instance.id:
                if not qs.exclude(id=instance.id).count():
                    return potential
        # we hit a conflicting slug, so bump the suffix & try again
        suffix += 1
