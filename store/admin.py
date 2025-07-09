from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Review, Wishlist, Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'status', 'coupon', 'discount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'coupon__code')
    list_editable = ('status',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('comment', 'product__name', 'user__username')

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist)