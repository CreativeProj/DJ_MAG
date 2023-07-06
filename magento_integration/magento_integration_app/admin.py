# Register your models here.
from django.contrib import admin
from .models import Category, Product, Cart,CartItem,Customer

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Customer)