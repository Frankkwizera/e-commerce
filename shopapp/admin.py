# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from shopapp.models import *

# Register your models here.

admin.site.register(Product)
admin.site.register(Seller)
admin.site.register(Category)
admin.site.register(Sale)
