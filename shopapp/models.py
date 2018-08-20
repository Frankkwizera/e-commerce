# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    """ Model to store category names """
    category_name = models.CharField(max_length=100, unique=True, help_text="Category name e.g: A series,J series")

    def __str__(self):
        return self.category_name

class Seller(models.Model):
    """ Model to store seller info """
    user = models.OneToOneField(User)
    first_name = models.CharField(max_length=100, help_text="First Name")
    second_name = models.CharField(max_length=100, help_text="Second Name")
    email = models.CharField(max_length=100,help_text="Email to receive on notification")
    phone_number = models.IntegerField(help_text="Phone number")

    def __str__(self):
        return str(self.first_name) + " " + str(self.second_name)


class Product(models.Model):
    """ Model to store Products in the shop """
    product_name = models.CharField(max_length=100, help_text="Name of the product")
    title_image = models.FileField(upload_to='media',)
    #second_image = models.FileField(upload_to='media', help_text="Optional", null=True,blank=True)
    #third_image = models.FileField(upload_to='media', help_text="Optional", null=True,blank=True)
    time = models.DateTimeField(help_text="Time when the product is uploaded")
    network = models.CharField(max_length=100)
    launch = models.CharField(max_length=100)
    display = models.CharField(max_length=100)
    os = models.CharField(max_length=100)
    storage = models.CharField(max_length=100)
    ram = models.CharField(max_length=100)
    front_camera = models.CharField(max_length=100)
    back_camera = models.CharField(max_length=100)
    battery = models.CharField(max_length=100)
    features = models.CharField(max_length=100)
    price = models.IntegerField(help_text="Price of the product")
    #quantity = models.IntegerField(help_text="quantity of this product available in your store")
    category = models.ForeignKey(Category)
    #seller = models.ForeignKey(Seller)

    def __str__(self):
        return str(self.product_name) +" " +str(self.price)

class Sale(models.Model):
    """ models to store sales request """
    first_name = models.CharField(max_length=100)
    second_name = models.CharField(max_length=100)
    phone_number = models.IntegerField(help_text="E.g: +250788776655")
    email = models.EmailField(max_length=70,help_text="E.g: you@gmail.com")
    address = models.CharField(max_length=100, help_text="E.g: remera")
    product = models.ForeignKey(Product)
    quantity = models.IntegerField(help_text="Quantity requested")
    time =  models.DateTimeField(help_text="Time when Product requested")
    sold = models.BooleanField(default =False)

    def __str__(self):
        return str(self.first_name) + " " + str(self.second_name) + " " + str(self.product)


class Document(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    upload = models.FileField()
