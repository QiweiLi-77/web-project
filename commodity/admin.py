from django.contrib import admin
from django.forms import ModelForm
from .models import Types, CommodityInfos
from django import forms
from django.db.models import Sum


class CommodityInfosForm(forms.ModelForm):
    """
    商品信息表单
    """

    class Meta:
        model = CommodityInfos
        fields = '__all__'


@admin.register(Types)
class TypesAdmin(admin.ModelAdmin):
    """
    商品类型管理
    """
    list_display = ['id', 'firsts', 'seconds']
    list_display_links = ['id']
    list_filter = ['firsts']
    search_fields = ['firsts', 'seconds']
    list_editable = ['firsts', 'seconds']


@admin.register(CommodityInfos)
class CommodityInfosAdmin(admin.ModelAdmin):
    """
    商品信息管理
    """
    form = CommodityInfosForm
    readonly_fields = ['sold', 'category_display']

    list_display = ['id', 'name', 'get_first_category', 'get_second_category', 'base_price', 'stock', 'sold', 'likes']
    search_fields = ['name', 'product_type__firsts', 'product_type__seconds']
    list_filter = ['created', 'product_type__firsts']

    fieldsets = (
        ('基本信息', {
            'fields': (
                'name', 'product_type', 'base_price', 'img', 'details', 'likes', 'category_display'),
        }),
        ('库存信息', {
            'fields': ('stock', 'sold'),
        }),
    )

    def get_first_category(self, obj):
        return obj.first_category

    get_first_category.short_description = 'First Category'
    get_first_category.admin_order_field = 'product_type__firsts'

    def get_second_category(self, obj):
        return obj.second_category

    get_second_category.short_description = 'Second Category'
    get_second_category.admin_order_field = 'product_type__seconds'

    def category_display(self, obj):
        return f"{obj.first_category} - {obj.second_category}"

    category_display.short_description = 'Category Display'

    def save_model(self, request, obj, form, change):
        # 保存模型
        super().save_model(request, obj, form, change)