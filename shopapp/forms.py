from django.forms import ModelForm
from shopapp.models import *
from django import forms

class SalesForm(ModelForm):

    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Sale
        exclude = ('time','product','quantity','sold',)

class ProductForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Product
        exclude = ('time','seller',)

class CategoryForm(ModelForm):
    error_css_class = "warning"
    required_css_class = "info"

    class Meta:
        model = Category
        fields = ('__all__')
