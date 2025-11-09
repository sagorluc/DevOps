from django.contrib import admin
from celery_app.models import Restaurant, SellerProfile

# Register your models here.
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['id', 'res_name']
    ordering = ['-id']
    
    
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'restaurant', 'role']
    ordering = ['-id']
    
    
admin.site.register(Restaurant, RestaurantAdmin)
admin.site.register(SellerProfile, SellerProfileAdmin)