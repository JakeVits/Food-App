from django.urls import path
from . import views
from .views import *


urlpatterns = [
	#Leave as empty string for base url
	path('login/', views.loginPage, name="login"),
	path('register/', views.registerPage, name="register"),
	path('logout/', views.logoutUser, name="logout"),

	path('', views.store, name="store"),
	path('cart/', views.cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),

	# path('update_item/', views.updateItem, name="update_item"),
	path('process_order/', views.processOrder, name="process_order"),

#customer urls
	path('profileDetails/', views.profileDetails, name="profileDetails"),
	path('orderHistory/', views.orderHistory, name="orderHistory"),
	path('editProfile/', views.editProfile, name="editProfile"),
	path('add-item/', views.add_item, name="add-item"),


#admin urls
	path('dashboard/', views.dashboard, name="dashboard"),

	path('add-customer/', views.add_customer, name="add-customer"),
	path('customer-list/', views.view_customer_list, name="customer-list"),
	path('customer-details/<pk>/', views.view_customer_details, name="customer-details"),
	path('update-customer/<pk>/', views.update_customer, name="update-customer"),
	path('delete-customer/<pk>/', views.delete_customer, name="delete-customer"),

	path('add-product/', views.addProduct, name="add-product"),
	path('product-list/', views.adminProductlist, name="adminProductlist"),
	path('view-product/<pk>/', views.view_product_details, name="view-product"),
	# path('update-product/<int:pk>/', views.editProduct, name="editProduct"),
    # path('deleteProduct/<str:pk>', views.deleteProduct, name="deleteProduct"),
	
	path('adminOrderlist/', views.adminOrderlist, name="adminOrderlist"),    
]