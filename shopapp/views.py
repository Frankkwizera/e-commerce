# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from shopapp.models import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from shopapp.forms import *
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.mail import EmailMessage
from django.db import IntegrityError
from slacker import Slacker
from django.contrib import auth
#from imp import reload
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
# Create your views here.

def index(request):
    context_dict = {}
    products = Product.objects.all().order_by('-time')
    categories = Category.objects.all()
    paginator = Paginator(products, 20) # limitting whats shown
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    pages = paginator.num_pages
    #left_pic = products[len(products)-1].title_image
    #right_pic = products[len(products)-2].title_image
    #mid_pic = products[0].title_image
    #context_dict['midpic'] = mid_pic
    #context_dict['leftpic'] = left_pic
    #context_dict['rightpic'] = right_pic
    context_dict['pages'] = pages
    context_dict['categories'] = categories
    context_dict['products'] = products

    #Initiating sesson when user lands on this function
    if request.session.has_key('products'):
        #print request.session['products']
        pass
    else:
        request.session['products'] = []

    return render(request, 'index.html', context_dict)

#function to render contact us template
def contact(request):
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    return render(request, 'contact.html', context_dict)

#function to render about us template
def aboutus(request):
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    return render(request, 'about.html', context_dict)

def contact_feedback(request):
    """ Function to send customer feedback to the seller """
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        message_to_send = message + " From " + str(name) + " With the following details "+ str(email)
        #Slack notification
        try:
            slack_notification("general",message)
        except:
            pass
        email = EmailMessage('Customer Feedback',message_to_send,to=['frankpmn@gmail.com'])
        email.send()

    return render(request, 'contact-success.html')

#function to render how to buy template
def howToBuy(request):
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    return render(request, 'how-to-buy.html', context_dict)

def category(request,category_id):
    """ function to sort products based on categories """
    context_dict = {}
    categories = Category.objects.all()
    category_choosen = Category.objects.filter(id=category_id).first()
    products = Product.objects.filter(category=category_choosen).order_by('-time')
    paginator = Paginator(products, 20) # limitting whats shown
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    pages = paginator.num_pages
    context_dict['pages'] = pages
    context_dict['categories'] = categories
    context_dict['products'] = products
    #print context_dict
    return render(request, 'index.html', context_dict)

def product_details(request,product_id):
    """ Function to render a specific product """
    context_dict = {}
    categories = Category.objects.all()
    product_choosen = Product.objects.filter(id= product_id).first()
    related_products = Product.objects.filter(category = product_choosen.category).exclude(id=product_id).order_by('-time')[:4]
    unrelated_products = Product.objects.filter().exclude(category = product_choosen.category).order_by('-time')[:4]
    context_dict['unrelatedProducts'] = unrelated_products
    context_dict['relatedProducts'] = related_products
    context_dict['categories'] = categories
    context_dict['product'] = product_choosen

    return render(request, 'single.html', context_dict)

@csrf_exempt
def add_to_cart(request):
    """ Function to add products to cart """
    #print "in the add cart function"
    if request.method == 'POST':
        product_id = request.POST.get('product_id', '')
        quantity = request.POST.get('quantity', '')
        #print product_id

        #Initiating sesson when user lands on this function
        if request.session.has_key('products'):
            #print request.session['products']
            pass
        else:
            request.session['products'] = []

        # saving product_id in the session for later use
        request.session['products'].append({'id':product_id,'quantity':quantity})


        request.session.save()
        #print request.session['products']
        product = Product.objects.filter(id=product_id).first()
    return HttpResponse(" Successfully Added " +str(quantity)+ " " + str(product.product_name) + " in the cart")

def checkout(request):
    """ Function to render Checkout Page """
    context_dict = checkout_data(request)

    #print context_dict
    #print "total is"
    #print type(context_dict['total'])
    try:
        if context_dict['total'] == 0:
            return render(request, 'empty-cart.html', context_dict)
    except KeyError:
        return redirect('/delete')

    return render(request, 'checkout.html', context_dict)

def empty(request):
    """ Function to deleted active session and start over """
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    if request.session.has_key('products'):
        del request.session['products']
    return render(request, 'empty-cart.html',context_dict)

@csrf_exempt
def cartvalue(request):
    """ Function to return nbr of elements in the cart """
    #print "in cart value function"
    if request.method == 'POST':
        value = 0
        if request.session.has_key('products'):
            value = len(request.session['products'])

    return HttpResponse(value)


def editsession(request):
    """ Function to edit session """
    if request.method == "POST":
        product_id = request.POST.get('product_id', '')
        quantity = request.POST.get('quantity', '')
        if request.session.has_key('products'):

             for i in request.session['products']:
                 if int(i['id']) == int(product_id):
                     i['quantity'] = quantity
                     request.session.save()
                     request.session.modified = True
    return HttpResponse("saved")


def sessionremove(request,product_id,quantity):
    """ Function to remove a product from a session """
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    if request.session.has_key('products'):
        for i in request.session['products']:
            if i['id'] == product_id and i['quantity'] == quantity:
                request.session['products'].remove(i)
                break
        request.session.save()
        #print type(len(request.session['products']))
        if len(request.session['products']):
            pass
        else:
            return render(request, 'empty-cart.html',context_dict)

    return redirect('/checkout')

def order(request):
    """ Function to Render order page and all it containing data """
    context_dict = checkout_data(request)
    saleform = SalesForm()
    context_dict['saleform'] = saleform
    return render (request, 'order.html',context_dict)


#utilty function
def checkout_data(request):
    context_dict = {}
    products = []
    if request.session.has_key('products'):
        products_requested = request.session['products']
        #print "product requested"
        #print products_requested
        for i in products_requested:
            print
            x = Product.objects.filter(id=i['id']).first()
            #print "printing x"
            #print x
            if x is None:
                #print "about to delete shit"
                return redirect('/delete')
            subtotal = int(x.price)*int(i['quantity'])
            #print "down here"
            products.append({'product':x,'quantity':i['quantity'],'subtotal':subtotal})
        #print products

        #determining total cost
        total = 0
        for k in products:
            #print "printing products"
            #print products
            total = total + (int(k['product'].price) * int(k['quantity']))
        #print total
        context_dict['total'] = total
        context_dict['products'] = products

    categories = Category.objects.all()
    context_dict['categories'] = categories
    #print "printing what is in the checkout function"
    #print context_dict
    return context_dict

def deletesession(request):
    """ Function to delete session """
    del request.session['products']

    return redirect('/')

#notification
def slack_notification(channel,message):
    slack = Slacker('xoxp-222894375042-223986280551-223786515910-218e1748e92a26a993487428479a6af9')

    if channel.startswith('#'):
        pass
    else:
        channel = '#'+channel

    slack.chat.post_message(channel,message)

def saveclient(request):
    """ Function to save a client """
    context_dict = {}

    categories = Category.objects.all()
    context_dict['categories'] = categories
    product_requests = []
    if request.session.has_key('products'):

        customer_name = ''
        customer_phone = ''
        customer_email = ''

        for i in request.session['products']:
            if request.method == 'POST':
                saleform = SalesForm(request.POST)
                if saleform.is_valid():
                    saleform = saleform.save(commit=False)
                    saleform.quantity = i['quantity']
                    product = Product.objects.filter(id=i['id']).first()
                    saleform.product = product
                    saleform.time = datetime.now()
                    saleform.sold = False
                    customer_name = str(saleform.first_name) + " " + str(saleform.second_name)
                    customer_phone = str(saleform.phone_number)
                    customer_email = str(saleform.email)
                    context_dict['customername'] = customer_name
                    saleform.save()
                    product_requests.append({'product':saleform.product,'quantity':saleform.quantity})
                    #print product_requests
                    #message = str(saleform.first_name) +' '+ str(saleform.second_name) + ' order for ' +str(saleform.quantity) +str(saleform.product)
                    #print message
                    """
                    try:
                        email = EmailMessage('SHOP ORDER', str())
                    except Exception,e:
                        pass
                    """
        #user = request.user
        #seller = Seller.objects.filter(user=user).first()
        #seller_email = seller.email
        string = ''
        for x in product_requests:
            string = string + str(x['quantity']) +' '+str(x['product'].product_name) +str(',')

        #seller notification
        message = str(customer_name) +" ordered for " + string +" Phone number is "+ customer_phone + " Email is "+customer_email

        #Slack notification
        try:
            slack_notification("general",message)
        except:
            pass

        email = EmailMessage('Shopping Order',message,to=['frankpmn@gmail.com','giramahoroclarisse.gc@gmail.com'])
        email.send()

        #customer notification
        message ="Thanks "+ str(customer_name) +"  ordered for " + string +" Phone number is "+ customer_phone + " Email is "+customer_email

    del request.session['products']
    request.session['products'] = []
    return render(request,"success.html", context_dict)

def search(request):
    """ Function to search products """
    context_dict = {}
    search = request.GET.get('search','')
    products = Product.objects.filter(product_name__contains = search).order_by('-time')
    categories = Category.objects.all()
    paginator = Paginator(products, 20) # limitting whats shown
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    pages = paginator.num_pages
    all_products = Product.objects.all().order_by('-time')
    #left_pic = all_products[len(all_products)-1].title_image
    #right_pic = all_products[len(all_products)-2].title_image
    #mid_pic = all_products[0].title_image
    length = len(products)
    context_dict['message'] = "Search results for "+str(search)
    context_dict['length'] = length
    context_dict['name'] = search
    #context_dict['midpic'] = mid_pic
    #context_dict['leftpic'] = left_pic
    #context_dict['rightpic'] = right_pic
    context_dict['pages'] = pages
    context_dict['categories'] = categories
    context_dict['products'] = products

    return render(request, 'index.html', context_dict)

def loginPage(request):
    """
    Function to render login page
    """
    if request.session.has_key('logged'):
        return redirect('/adminProducts')
    return render(request,'login.html')

def log_in(request):
    """ Validating a user """
    context_dict = {}
    if request.method == 'POST':
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        user = auth.authenticate(username = username,password=password)
        if user is not None:
            if user.is_active:
                auth.login(request,user)
                request.session['logged'] = True
                request.session.save()
                return redirect('/adminProducts')
                #return redirect(request.POST.get('next','/adminProducts'))
            else:
                context_dict['message'] = "Please contact system Admin"
        else:
            context_dict['message'] = "invalid username or password"
    return render(request, 'login.html',context_dict)

@login_required(login_url='/loginpage/')
def adminProducts(request):
    """ Function to render admin page """
    context_dict = {}
    categories = Category.objects.all()
    sales = Sale.objects.filter(sold=False).order_by('-time')
    context_dict['salelength'] = len(sales)
    context_dict['categories'] = categories
    products = Product.objects.all().order_by('-time')
    context_dict['products'] = products
    context_dict['length'] = len(products)
    context_dict['catLength'] = len(categories)
    productform = ProductForm()
    context_dict['productform'] = productform
    context_dict['user'] = request.user
    #print context_dict
    return render(request, 'admin.html',context_dict)

@login_required(login_url='/loginpage/')
def adminCategory(request):
    """ Function to render admin page """
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    products = Product.objects.all().order_by('-time')
    context_dict['products'] = products
    context_dict['catLength'] = len(categories)
    context_dict['length'] = len(products)
    sales = Sale.objects.filter(sold=False).order_by('-time')
    context_dict['salelength'] = len(sales)
    context_dict['user'] = request.user
    categoryform = CategoryForm()
    context_dict['categoryform'] = categoryform
    return render(request, 'category.html',context_dict)

@login_required(login_url='/loginpage/')
def addProduct(request):
    """ Function to add a product """
    if request.method == 'POST':
        productform = ProductForm(request.POST,request.FILES)
        if productform.is_valid():
            productform = productform.save(commit=False)
            productform.time = datetime.now()
            user = request.user
            #productform.seller = Seller.objects.filter(user=user).first()
            productform.save()
    return redirect('/adminProducts')

@login_required(login_url='/loginpage/')
def addCategory(request):
    """ Function to add a product """
    if request.method == 'POST':
        categoryform = CategoryForm(request.POST)
        if categoryform.is_valid():
            categoryform = categoryform.save(commit=False)
            categoryform.save()
    return redirect('/adminCategory')

@login_required(login_url='/loginpage/')
def editProduct(request,product_id=1):
    """ Function to edit product """
    context_dict = {}
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-time')

    if request.method == 'POST':
        product_id = request.POST.get('product_id','')
        instance = get_object_or_404(Product, id=product_id)
        productform = ProductForm(request.POST, request.FILES or None, instance = instance)
        if productform.is_valid():
            product = productform.save(commit=False)
            product.save()
            return redirect('/adminProducts')

    productform = ProductForm()
    instance = get_object_or_404(Product, id=product_id)
    productform = ProductForm(instance = instance)

    sales = Sale.objects.filter(sold=False).order_by('-time')
    context_dict['salelength'] = len(sales)
    context_dict['instance_id'] = instance.id
    context_dict['name'] = instance.product_name
    context_dict['categories'] = categories
    context_dict['products'] = products
    context_dict['catLength'] = len(categories)
    context_dict['length'] = len(products)
    context_dict['productform'] = productform
    context_dict['user'] = request.user
    return render(request, 'admin.html', context_dict)


@login_required(login_url='/loginpage/')
def editCategory(request,category_id=1):
    """ Function to edit category """
    context_dict = {}
    context_dict['user'] = request.user
    categories = Category.objects.all()
    products = Product.objects.all().order_by('-time')
    if request.method == 'POST':
        #print "in the post"
        category_id = request.POST.get('category_id','')
        #print "category_id is"
        #print category_id
        instance = get_object_or_404(Category, id=category_id)
        #print instance
        categoryform = CategoryForm(request.POST, instance = instance)
        if categoryform.is_valid():
            category = categoryform.save(commit=False)
            category.save()
            return redirect('/adminCategory')

    categform = CategoryForm()
    instance = get_object_or_404(Category, id=category_id)
    categoryform = CategoryForm(instance = instance)

    sales = Sale.objects.filter(sold=False).order_by('-time')
    context_dict['salelength'] = len(sales)
    context_dict['instance_id'] = instance.id
    context_dict['name'] = instance.category_name
    context_dict['categories'] = categories
    context_dict['products'] = products
    context_dict['catLength'] = len(categories)
    context_dict['length'] = len(products)
    context_dict['categoryform'] = categoryform
    return render(request, 'category.html', context_dict)


@login_required(login_url='/loginpage/')
def deletecategory(request,category_id):
    category = Category.objects.filter(id=category_id).first()
    category.delete()
    return redirect('/adminCategory')

@login_required(login_url='/loginpage/')
def deleteproduct(request,product_id):
    product = Product.objects.filter(id=product_id).first()
    product.delete()
    return redirect('/adminProducts')

@login_required(login_url='/loginpage/')
def sale_requests(request):
    """ Function to render request """
    context_dict = {}
    categories = Category.objects.all()
    context_dict['categories'] = categories
    products = Product.objects.all().order_by('-time')
    context_dict['products'] = products
    context_dict['catLength'] = len(categories)
    context_dict['length'] = len(products)
    sales = Sale.objects.filter(sold=False).order_by('-time')
    context_dict['sales'] = sales
    context_dict['salelength'] = len(sales)
    context_dict['user'] = request.user
    return render(request, 'sale-request.html',context_dict)


@login_required(login_url='/loginpage/')
def sold(request,sale_id):
    """Function to update sold out products """
    sale = Sale.objects.filter(id=sale_id).first()
    product = sale.product
    quantity = sale.quantity
    #print " sale id is " + str(sale_id)
    #print " product id is " + str(product.id)
    #print " quantity is " + str(quantity)
    if quantity > product.quantity:
        product.quantity = 0
        product.save()
    else:
        product.quantity = product.quantity - quantity
        product.save()
    sale.sold = True
    sale.save()
    return redirect('/sales')

def logout(request):
    """function to logout a user"""
    auth.logout(request)
    if 'logged' in request.session:
        del request.session['logged']
    return redirect('/login')

def signup(request):
    """
    Function for Signing Up a new User"""

    context_dict ={}

    if request.method == 'POST':
        first_name = request.POST.get('firstname', '')
        second_name = request.POST.get('secondname', '')
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phonenumber', '')
        password = request.POST.get('password', '')
        Repassword = request.POST.get('Repassword', '')


        if  password == Repassword:
            pass
        else:
            context_dict['ErrorMessage'] = "Password didn't match"
            return render(request,'login.html',context_dict)

        try:
            user = User.objects.create_user(username = user_name, password = password)
            seller = Seller.objects.create(user = user,
                                           first_name = first_name,
                                           second_name= second_name,
                                           email = email,
                                           phone_number = int(phone),)
            seller.save()
            user = auth.authenticate(username = user_name,password = password)
            auth.login(request,user)
        except IntegrityError:
            context_dict['ErrorMessage'] = "This User Name already exists"
            return render(request,'login.html',context_dict)
        except:
            context_dict['ErrorMessage'] = "Server Error contact system Developers"
            return render(request,'login.html',context_dict)

    return redirect('/adminProducts')
