from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.base import Model
from django.db.models.deletion import CASCADE, SET_NULL
from django.db.models.expressions import F
from django.urls import reverse
from django.core.validators import RegexValidator
# Create your models here.

class Customer(models.Model):
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(validators=[RegexValidator(regex=r"^\+?1?\d{8,15}$")], max_length=16, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    profile_image = models.ImageField(upload_to='customer-image', default="customer-image/profile.png", null=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    seller = models.ForeignKey(Customer, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(max_length=500)
    product_image = models.ImageField(upload_to='product-image')
    closed_date = models.DateField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return self.product.name

    @property
    def get_total_items(self):
        total = 0
        items = Cart.objects.filter(customer=self.customer).values('quantity') # returns as a dictionary
        for item in items:
            total += item['quantity']
        return total

    @property
    def get_total_price(self):
        price = 0
        products = Cart.objects.filter(customer=self.customer) # returns as a dictionary
        for item in products:
            price += item.product.price * item.quantity
        return price


class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Delivered','Delivered'),
        ('Cancelled', 'Cancelled')       
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
    address = models.CharField(max_length=50)
    city = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    zipcode = models.CharField(max_length=10)
    country = models.CharField(max_length=30)
    ordered_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS)
    
    def __str__(self):
        return f'Ordered ID = {str(self.id)}, Customer = {self.customer.user.username}'


class Item(models.Model):
    order = models.ForeignKey(Order, on_delete=CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=SET_NULL, null=True)
    
    def __str__(self):
        return f'{self.order.customer} ordered {self.product.name}'

class Quantity(models.Model):
    item = models.OneToOneField(Item, on_delete=CASCADE, null=True)
    quantity = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.item.product.name} Quantity = {str(self.quantity)}"



    # @property
    # def shipping(self):
    #     shipping = False
    #     orderitems = self.orderitem_set.all()
    #     for i in orderitems:
    #         if i.product.digital == False:
    #             shipping = True
    #     return shipping

    # @property
    # def get_cart_total(self):
    #     orderitems = self.orderitem_set.all()
    #     total = sum ([item.get_total for item in orderitems])
    #     return total

    # @property
    # def get_cart_items(self):
    #     orderitems = self.orderitem_set.all()
    #     total = sum ([item.quantity for item in orderitems])
    #     return total

# class OrderItem(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
#     quantity = models.IntegerField(default=0, null=True, blank=True)
#     date_added = models.DateTimeField(auto_now_add=True)

#     @property
#     def get_total(self):
#         total = self.product.price * self.quantity
#         return total

# class ShippingAddress(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True)
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
#     address = models.CharField(max_length=50)
#     city = models.CharField(max_length=20)
#     state = models.CharField(max_length=20)
#     zipcode = models.CharField(max_length=10)
#     added_date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.address

    # @property
    # def shipping(self):
    #     shipping = False
    #     orderitems = self.orderitem_set.all()
    #     for i in orderitems:
    #         if i.product.digital == False:
    #             shipping = True
    #     return shipping