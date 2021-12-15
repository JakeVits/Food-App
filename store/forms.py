from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import Product, Customer

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email','password1','password2']

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2', 'email']:
            self.fields[fieldname].help_text = None

class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = '__all__'
		exclude = ['user']

class editProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ['name','price','description','date_delivery','date_closed','product_image']
