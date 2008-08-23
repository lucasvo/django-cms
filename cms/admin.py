from django.contrib import admin
from cms import models


class PageAdmin(admin.ModelAdmin):
    prepopulated_fields = {'title': ['slug',] }


admin.site.register(models.Page, PageAdmin)

