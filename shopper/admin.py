from django.contrib import admin
from .models import *

@admin.register(CartInfos)
class CartInfosAdmin(admin.ModelAdmin):
    """
    购物车管理界面配置
    Shopping cart admin interface configuration
    """
    list_display = ['id', 'quantity']


@admin.register(OrderInfos)
class OrderInfosAdmin(admin.ModelAdmin):
    """
    订单管理界面配置
    Order admin interface configuration
    """
    list_display = ['id', 'price', 'created', 'state']
    list_filter = ['state']  # 状态过滤器 / Status filter
    date_hierarchy = 'created'  # 日期层次结构 / Date hierarchy


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    """
    配送地址管理界面配置
    Delivery address admin interface configuration
    """
    list_display = ['id', 'user_id', 'recipient_name', 'city', 'region', 'is_default']
    list_filter = ['is_default', 'country', 'region']
    search_fields = ['recipient_name', 'address_line1', 'city', 'postal_code']