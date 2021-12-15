from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.urls import reverse
# Create your models here.

class Customer(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    # name = models.CharField(max_length=200, null=True)
    # email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    profile_image = models.ImageField(upload_to='customer-image', default="customer-image/profile.png", null=True, blank=True)

    def __str__(self):
        return self.user.username
        
    # @property
    # def profileimageURL(self):
    #     try:
    #         url = self.profile_image.url
    #     except:
    #         url = ''
    #     return url

class Product(models.Model):
    seller = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.FloatField()
    description = models.TextField()
    # digital = models.BooleanField(default=False, null=True, blank=False)
    product_image = models.ImageField(upload_to='product-image')
    date_added = models.DateTimeField(auto_now_add=True)
    date_delivery = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)
    date_closed = models.DateTimeField(auto_now_add=False, auto_now=False, null=True, blank=True)

    def __str__(self):
        return self.name

    # @property
    # def imageURL(self):
    #     try:
    #         url = self.product_image.url
    #     except:
    #         url = ''
    #     return url

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Out Of Delivery', 'Out Of Delivery'),
        ('Delivered','Delivered')
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True)
    status = models.CharField(max_length=200, choices=STATUS)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum ([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum ([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
        return shipping