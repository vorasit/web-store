from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review, Wishlist

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'tracking_number', 'shipping_company', 'created_at')
    list_filter = ('status', 'shipping_company', 'created_at')
    search_fields = ('id', 'user__username', 'tracking_number', 'shipping_company')
    list_editable = ('status', 'tracking_number', 'shipping_company')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'product__name', 'user__username')

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist)