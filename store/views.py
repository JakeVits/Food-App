from django.core.files.base import File
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.urls.base import reverse_lazy
from .models import *
from django.http import JsonResponse
import json
import datetime	

from django.views.generic import View, TemplateView
from .forms import CreateUserForm, ProductForm, CustomerForm, editProductForm
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.contrib.auth.mixins import LoginRequiredMixin


# @unauthenticated_user
def registerPage(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			Customer.objects.create(user=user).save()
			# group = Group.objects.get(name='customer')
			# user.groups.add(group)
			messages.success(request, 'Account was created for ' + username)
			return redirect('register')
		messages.warning(request, 'Account Creation Failed')
	context = {'form': form}
	return render(request, 'accounts/register.html', context)

# @unauthenticated_user
def loginPage(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			if request.user.is_superuser:
				return redirect('dashboard')
			return redirect('store')
		else:
			messages.info(request, 'Username or Password is Incorrect')
	return render(request, 'accounts/login.html')

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
def store(request):
	if not request.user.is_staff:
		user = Customer.objects.get(user=request.user)
	cartItems = ''
	try:
		user_order = Order.objects.filter(customer=user).first()
		print(user_order)
		order = Order.objects.get(id=user_order.id)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items		
	except:
		print('No order is made')
	# else:
	# 	items = []
	# 	order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	# 	cartItems = order['get_cart_items']
	products = Product.objects.all()
	context = {'products': products, 'cartItems': cartItems}
	return render(request, 'store/store.html', context)

@login_required(login_url='login')
def cart(request):
	try:
		user = Customer.objects.get(user=request.user)
		user_order = Order.objects.filter(customer=user).first()
		order = Order.objects.get(id=user_order.id)	
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
		# orders = Order.objects.filter(customer=customer, complete=False)
	except:
		print('No orders are added into cart')
		items, order, cartItems = None, None, None
	context = {'items': items, 'order':order, 'cartItems': cartItems }
	return render(request, 'store/cart.html', context)

class CheckOutView(LoginRequiredMixin):
	pass

@login_required(login_url='login')
def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
		orders = Order.objects.filter(customer=customer, complete=False)
	else:
		items = []
		order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}
		cartItems = order['get_cart_items']
	context = {'items':items,'order':order,'cartItems':cartItems }
	return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def add_item(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)
	customer = request.user.customer
	# user = Customer.objects.get(user=request.user)
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, product=product, complete=False)
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove' :
		orderItem.quantity = (orderItem.quantity - 1)
	orderItem.save()
	if orderItem.quantity <= 0:
		orderItem.delete()
	return JsonResponse('Item was added', safe=False)

@login_required(login_url='login')
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)
	customer = request.user.customer
	order,created = Order.objects.get_or_create(customer=customer, complete=False)
	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)
	return JsonResponse('Order Complete!', safe=False)

@login_required(login_url='login')
def orderHistory(request):
	orders = Order.objects.filter(customer=request.user.customer)
	# OrderItem.objects.filter(order=or)
	context = {'orders': orders}
	return render(request, 'customer/orderHistory.html', context)	



#admin view
@login_required(login_url='login')
# @admin_only
def dashboard(request):
	context = {}
	return render(request, 'admin/dashboard.html', context)

@login_required(login_url='login')
# @admin_only
def view_customer_list(request):
	customers = Customer.objects.all()
	# customer = request.user.customer
	context = {'customers': customers}
	return render(request, 'admin/customer_list.html', context)

@login_required(login_url='login')
# @admin_only
def update_customer(request, pk):
	orders = Order.objects.all()
	total_orders = orders.count()
	customer = Customer.objects.get(id=pk)
	form = CreateUserForm(instance=customer.user)
	context = {'customer': customer, 'total_orders': total_orders, 'form': form}
	if request.method == 'POST':
		updateForm = CreateUserForm(request.POST, instance=customer.user)	
		if updateForm.is_valid():
			updateForm.save()
			messages.success(request, 'Account is Updated Successfully')
			return redirect(reverse('customer', args=[pk]))
		messages.warning(request, 'Update Failed!')
		return redirect(reverse('update-customer', args=[pk]))	
	return render(request, 'admin/customer_update.html', context)

@login_required(login_url='login')
# @admin_only
def add_customer(request):
	customer = Customer.objects.all()
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():		
			user = form.save()	
			# username = form.cleaned_data.get('username')
			# group = Group.objects.get(name='customer')
			# user.groups.add(group)
			#Added username after video because of error returning customer name if not added
			Customer.objects.create(user=user).save()
			messages.success(request, f'Account was created for {form.cleaned_data["username"]}')
			return redirect('customer-create')
	context = {'form':form, 'customer':customer}
	return render(request, 'admin/customer_create.html', context)

@login_required(login_url='login')
# @admin_only
def view_customer_details(request, pk):
	customer = Customer.objects.get(id=pk)
	form = CustomerForm(instance=customer)
	if request.method == 'POST':	
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			form.save()
			return redirect('customer-list')
	context = {'form':form, 'customer': customer}
	return render(request, 'admin/customer_details.html', context)

@login_required(login_url='login')
# @admin_only
def delete_customer(request, pk):
	customer = Customer.objects.get(id=pk)
	if request.method == 'POST':
		customer.delete()
		return redirect('customer-list')
	context = {'customer':customer}
	return render(request, 'admin/customer-delete.html', context)


@login_required(login_url='login')
# @admin_only
def adminProductlist(request):
	products = Product.objects.all()
	context = {'products':products}
	return render(request, 'admin/adminProductlist.html', context)

@login_required(login_url='login')
def view_product_details(request, pk):
	product = Product.objects.get(id=pk)
	context = {'product': product}
	return render(request, 'admin/adminProductdetails.html',context)

@login_required(login_url='login')
# @admin_only
def addProduct(request):
	products = Product.objects.all()
	form = ProductForm()
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			return redirect('adminProductlist')
	context = {'form': form, 'products': products}
	return render(request, 'admin/adminProductadd.html', context)




@login_required(login_url='login')
# @admin_only
def adminOrderlist(request):
	orders = OrderItem.objects.all()
	context = {'orders':orders}
	return render(request, 'admin/adminOrderlist.html', context)

@login_required(login_url='login')
# @admin_only
def editProduct(request, pk):
	product = Product.objects.get(id=pk)
	form = editProductForm(instance=product)

	if request.method == 'POST':
		form = editProductForm(request.POST, instance=product)
		if form.is_valid():
			form.save()
			return redirect('adminProductlist')

	context = {'form':form,'product':product}
	return render(request, 'admin/adminProductedit.html', context)

@login_required(login_url='login')
# @admin_only
def deleteProduct(request, pk):
	product = Product.objects.get(id=pk)
	if request.method == 'POST':
		product.delete()
		return redirect('adminProductlist')

	context = {'product':product}
	return render(request, 'admin/adminProductdelete.html', context)



#customer view
@login_required(login_url='login')
def profileDetails(request):
	print('current user-->', request.user.id)
	user, order, total_price = '', '', 0
	try:		
		user = Customer.objects.get(user=request.user)
		total_order = Order.objects.filter(customer=user).count()
		try:
			prices = Product.objects.filter(seller=user)
			print(prices)
			for price in prices:
				print(price)
			# print(total_price.get_cart_items)
		except:
			print('===>Total spent money error<===')
		# print(price)
	except:
		user, order = None, None
		print('Error!')
	# orders = Order.objects.all()
	# 	customer = request.user.customer
	# 	total_orders = orders.count()
	# 	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	# 	items = order.orderitem_set.all()
	# 	cartItems = order.get_cart_items
	# else:
	# 	items = []
	# 	order = {'get_cart_total':0,'get_cart_items':0,'shipping':False}
	# 	cartItems = order['get_cart_items']
	context = {'customer': user, 'total_orders': total_order, 'total_price': total_price}
	return render(request, 'customer/profile.html', context)

@login_required(login_url='login')
def editProfile(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer,)
		if form.is_valid():
			form.save()
			messages.success(request, 'Account was Updated.')
			return redirect('profileDetails')
	context = {'form':form,'customer':customer}
	return render(request, 'customer/editProfile.html', context)



