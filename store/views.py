from datetime import datetime
from django.db.models.expressions import F
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import *
from django.http import JsonResponse
import json
from .forms import OrderForm, RegistrationForm, ProductForm, CustomerForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import serializers


################################## User Registration ##############################################
def registerPage(request):
	form = RegistrationForm()
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			Customer.objects.create(user=user).save()
			messages.success(request, 'Hello ' + username)
			user = authenticate(request, username=username, password=password)
			if user is not None:
				login(request, user)
				return redirect('store')
			return redirect('register')
		error = form.error_messages
		for e in error:
			error = error[e]
		messages.warning(request, f'{error}')
		return redirect('register')
	context = {'form': form}
	return render(request, 'accounts/register.html', context)

###################################### User Login ######################################
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

#################################### User Logout #######################################
def logoutUser(request):
	logout(request)
	return redirect('login')

################################### Total Cart Items ###################################
def fetch_cart_items(request):
	total_items = ''
	try:
		customer = Customer.objects.get(user=request.user)
		user = Cart.objects.filter(customer=customer).values('id')[0]
		user = Cart.objects.get(id=user['id'])
		total_items = user.get_total_items	
	except:
		print('------------->No Item is added to the cart')
	return total_items
################################### Total Price ###########################################
def fetch_total_price(request):
	total_price = 0
	try:
		customer = Customer.objects.get(user=request.user)
		user = Cart.objects.filter(customer=customer).values('id')[0]
		user = Cart.objects.get(id=user['id'])
		total_price = user.get_total_price 	
	except:
		print('------------->No Item is added to the cart')
	return total_price
#################################### Food Menu #############################################
@login_required(login_url='login')
def store(request):
	products = Product.objects.all()
	# for p in products:
	# 	if p.closed_date >= datetime.now().date():
	# 		print('Expire')
		# if p.closed_date >= datetime.now():
			# print('Expired ')
	context = {'products': products, 'cartItems': fetch_cart_items(request), 'date': datetime.now().date()}
	return render(request, 'store/store.html', context)

################################## Cart ##############################################
@login_required(login_url='login')
def display_cart(request):
	if request.user.is_staff:
		return render(request, 'admin/dashboard.html')
	user = Customer.objects.get(user=request.user)
	items = Cart.objects.filter(customer=user)	
	context = {'items': items, 'total_price': fetch_total_price(request), 'cartItems': fetch_cart_items(request)}
	return render(request, 'store/cart.html', context)

################################## Checkout ###########################################
@login_required(login_url='login')
def checkout(request):
	customer = Customer.objects.get(user=request.user)
	context = {'cartItems': fetch_cart_items(request), 'total_price': fetch_total_price(request)}
	if request.method == 'POST':
		form = OrderForm(request.POST)
		if form.is_valid():
			order = form.save()
			# to transfer cart items to order table
			cart = Cart.objects.filter(customer=customer)
			for cart in cart:
				item = Item.objects.create(order=order, product=cart.product)
				Quantity.objects.create(item=item, quantity=cart.quantity)	
			Cart.objects.filter(customer=customer).delete()			
			return redirect('store')
		error = form.errors
		for e in error:
			error = e
		messages.warning(request, error + ' is not valid')
		return redirect('checkout')
	return render(request, 'store/checkout.html', context)

################################# Action ################################################
@login_required(login_url='login')
def manage_cart(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action ---->', action)
	print('Product ID ---->', productId)
	if action == 'add':
		add_item(request, productId)
	else:
		remove_item(request, productId)
	return JsonResponse('Action Made', safe=False)

############################### Sort Order History ##############################
@login_required(login_url='login')
def sort_data(request):
	option = request.POST.get('option')
	orders = None
	if option == 'dd':
		orders = Order.objects.filter(customer=request.user.customer).order_by('-ordered_date')
	else:
		orders = Order.objects.filter(customer=request.user.customer)
	return render(request, 'customer/orderHistory.html', {'orders': orders})

################################# Add Item to Cart ############################################
@login_required(login_url='login')
def add_item(request, product_id):
	customer = None
	if request.user.is_staff:
		return 
	else:
		customer = Customer.objects.get(user=request.user)
	product = Product.objects.get(id=product_id)
	cart = Cart.objects.filter(customer=customer)
	if cart:
		existed_item = Cart.objects.filter(customer=customer, product=product)
		if existed_item:
			existed_item.update(quantity=F('quantity') + 1)
		else:
			Cart.objects.create(customer=customer, product=product, quantity=1).save()
	else:
		Cart.objects.create(customer=customer, product=product, quantity=1)	

########################################### Remove item from cart ###########################################
def remove_item(request, product_id):
	customer = Customer.objects.get(user=request.user)
	product = Product.objects.get(id=product_id)
	existed_item = Cart.objects.filter(customer=customer, product=product)
	existed_item.update(quantity=F('quantity') - 1)
	item = existed_item.values('quantity')[0]['quantity']	
	if item <= 0:
		existed_item.delete()				

############################################# View Ordered History ##################################################
@login_required(login_url='login')
def view_history(request):
	orders = Order.objects.filter(customer=Customer.objects.get(user=request.user))
	if orders:
		items = [order for order in orders]
		items = Item.objects.filter(order__in=items)
		context = {'orders': orders, 'items': items}
	return render(request, 'customer/orderHistory.html', context)	

############################################ View Ordered Products ##############################################
def view_product_history(request, pk):
	items = Item.objects.filter(order=pk)
	quantity = Quantity.objects.filter(item__in=items)
	return render(request, 'customer/itemDetails.html', {'items': zip(items, quantity)})

################################## Admin Customer Management #################################################
################################## Dashboard ##########################################################
@login_required(login_url='login')
def dashboard(request):
	return render(request, 'admin/dashboard.html')

############################################### View Customer #############################################
@login_required(login_url='login')
def view_customer_list(request):
	customers = Customer.objects.all()
	context = {'customers': customers}
	return render(request, 'admin/customer_list.html', context)

#################################### Update Customer ##################################################
@login_required(login_url='login')
def update_customer(request, pk):
	# orders = Order.objects.filter(customer=pk)
	# total_orders = orders.get_total_items
	# 'total_orders': total_orders,
	customer = Customer.objects.get(user=pk)
	form = CustomerForm(instance=customer.user)
	context = {'customer': customer, 'form': form}
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES or None, instance=customer.user)	
		if form.is_valid():
			form.save()
			customer.phone = form.cleaned_data['phone']
			customer.gender = form.cleaned_data['gender']
			customer.save()
			messages.success(request, f'{customer.user.username} profile is updated successfully')
			return redirect(reverse('update-customer', args=[pk]))
		error = form.errors
		for e in error:
			error = e
		messages.warning(request, error + ' is not valid')
		return redirect(reverse('update-customer', args=[pk]))	
	return render(request, 'admin/customer_update.html', context)

######################################## Create Customer By Admin ###########################################
@login_required(login_url='login')
def create_customer(request):
	customer = Customer.objects.all()
	form = RegistrationForm()
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():		
			user = form.save()	
			Customer.objects.create(user=user).save()
			messages.success(request, f'Account was created for {form.cleaned_data["username"]}')
			return redirect('create-customer')
		error = form.error_messages
		for e in error:
			error = e
		messages.warning(request, error)
		return redirect('create-customer')
	context = {'form':form, 'customer':customer}
	return render(request, 'admin/customer_create.html', context)

######################################### View Customer ####################################################
@login_required(login_url='login')
def view_customer_details(request, pk):
	customer = Customer.objects.get(user=pk)
	context = {'customer': customer}
	return render(request, 'admin/customer_details.html', context)

####################################### Delete Customer ################################################
@login_required(login_url='login')
def delete_customer(request, pk):
	customer = User.objects.get(id=pk)
	if request.method == 'POST':
		customer.delete()
		return redirect('list-customer')
	context = {'customer': customer}
	return render(request, 'admin/customer_delete.html', context)

####################################### Product Management ######################################
###################################### Product List ###########################################
@login_required(login_url='login')
def admin_product_list(request):
	products = Product.objects.all()
	context = {'products': products}
	return render(request, 'admin/adminProductlist.html', context)
######################################## View Product #############################################
@login_required(login_url='login')
def view_product_details(request, pk):
	product = Product.objects.get(id=pk)
	context = {'product': product}
	return render(request, 'admin/adminProductdetails.html',context)

############################################### Create Product ##############################################
@login_required(login_url='login')
def create_product(request):
	products = Product.objects.all()
	form = ProductForm()
	if request.method == 'POST':
		form = ProductForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, 'Product is created successfully')
			return redirect('admin-product-list')
		error = form.errors
		for e in error:
			error = e
		messages.warning(request, f'{e} is not valid')
		return redirect('create-product')
	context = {'form': form, 'products': products}
	return render(request, 'admin/adminProductadd.html', context)

##################################### Delete Product #############################################
def delete_product(request, pk):
	product = Product.objects.get(id=pk)
	if request.method == 'POST':
		product.delete()
		return redirect('admin-product-list')
	context = {'product':product}
	return render(request, 'admin/adminProductdelete.html', context)

##################################### Update Product #############################################
def update_product(request, pk):
	product = Product.objects.get(id=pk)
	form = ProductForm(instance=product)
	if request.method == 'POST':
		form = ProductForm(request.POST, instance=product)
		if form.is_valid():
			form.save()
			messages.success(request, 'Product is updated successfully')
			return redirect(reverse('update-product', args=[pk]))
		error = form.errors
		for e in error:
			error = e
		messages.warning(request, f'Invalid {error}' )
		return redirect(reverse('update-product', args=[pk]))
	context = {'form':form,'product':product}
	return render(request, 'admin/adminProductedit.html', context)


####################################### Order Management ############################################
###################################### Order List ########################################
@login_required(login_url='login')
# @admin_only
def adminOrderlist(request):
	orders = Order.objects.all()
	context = {'orders':orders}
	return render(request, 'admin/adminOrderlist.html', context)

########################################### Update Order #################################################
def update_order(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			messages.success(request, 'Order is updated successfully')
			return redirect(reverse('update-order', args=[pk]))
		error = form.errors
		for e in error:
			error = e
		messages.warning(request, f'Invalid {error}' )
		return redirect(reverse('update-product', args=[pk]))
	context = {'form': form}
	return render(request, 'admin/order_update.html', context)

############################################# Delete Order ##############################################
@login_required(login_url='login')
def delete_order(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		order.delete()
		return redirect('adminOrderlist')
	context = {'order': order}
	return render(request, 'admin/order_delete.html', context)


@login_required(login_url='login')
def manage_profile(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	orders = Order.objects.filter(customer=customer).count()
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			form.save()
			messages.success(request, 'Account was Updated.')
			return redirect('profileDetails')
	context = {'form': form, 'customer': customer, 'total_orders': orders}
	return render(request, 'customer/profile.html', context)

######################################## Edit Profile #######################################
@login_required(login_url='login')
def editProfile(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES, instance=customer)
		if form.is_valid():
			customer = form.save(commit=False)
			form.save()
			messages.success(request, 'Account was Updated.')
		return redirect('profile')
	context = {'form':form,'customer':customer}
	return render(request, 'customer/editProfile.html', context)
