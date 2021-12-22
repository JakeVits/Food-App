from django.urls import path
from . import views
from .views import *


urlpatterns = [
	#Leave as empty string for base url
	path('login/', views.loginPage, name="login"),
	path('register/', views.registerPage, name="register"),
	path('logout/', views.logoutUser, name="logout"),

	path('', views.store, name="store"),
	path('cart/', views.display_cart, name="cart"),
	path('checkout/', views.checkout, name="checkout"),
	# path('process_order/', views.process_order, name="process_order"),

#customer urls
	path('profile/', views.manage_profile, name="profile"),
	path('ordered-history/', views.view_history, name="history"),
	path('ordered-products/<pk>/', views.view_product_history, name="ordered-products"),
	path('editProfile/', views.editProfile, name="editProfile"),
	path('manage-cart/', views.manage_cart, name="manage-cart"),
	path('sort-data/', views.sort_data, name="sort-data"),

#admin urls
	path('dashboard/', views.dashboard, name="dashboard"),
	path('add-customer/', views.create_customer, name="create-customer"),
	path('customer-list/', views.view_customer_list, name="list-customer"),
	path('customer-details/<pk>/', views.view_customer_details, name="view-customer"),
	path('update-customer/<pk>/', views.update_customer, name="update-customer"),
	path('delete-customer/<pk>/', views.delete_customer, name="delete-customer"),

	path('create-product/', views.create_product, name="create-product"),
	path('admin-product-list/', views.admin_product_list, name="admin-product-list"),
	path('view-product/<pk>/', views.view_product_details, name="view-product"),
	path('update-product/<pk>/', views.update_product, name="update-product"),
    path('delete-product/<pk>', views.delete_product, name="delete-product"),

	path('delete-order/<pk>/', views.delete_order, name="delete-order"),
	path('update-order/<pk>/', views.update_order, name="update-order"),
	path('adminOrderlist/', views.adminOrderlist, name="adminOrderlist"),

]