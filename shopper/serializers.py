from django.utils import timezone

from rest_framework import serializers
from .models import CartInfos, OrderInfos, OrderItem, DeliveryAddress


class CartInfosSerializer(serializers.ModelSerializer):
    """
    购物车信息序列化器
    Shopping cart information serializer
    """
    class Meta:
        model = CartInfos
        fields = '__all__'
        # 参数depth是根据外键关联实现序列化嵌套功能
        # The depth parameter implements serialization nesting based on foreign key associations
        depth = 1


class OrderItemSerializer(serializers.ModelSerializer):
    """
    订单项目序列化器
    Order item serializer
    """

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product_name', 'price', 'quantity']


class OrderInfosSerializer(serializers.ModelSerializer):
    """
    订单信息序列化器
    Order information serializer
    """
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address_details = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = OrderInfos
        fields = ['id', 'price', 'created', 'state', 'payment_id', 'payment_method',
                  'delivery_address', 'delivery_address_details', 'items']

    def get_created(self, obj):
        if timezone.is_naive(obj.created):
            # 如果是naive datetime，先转换为aware
            aware_datetime = timezone.make_aware(obj.created)
            return timezone.localtime(aware_datetime).strftime("%Y-%m-%d %H:%M")
        return timezone.localtime(obj.created).strftime("%Y-%m-%d %H:%M")

    def get_delivery_address_details(self, obj):
        if obj.delivery_address:
            return {
                'recipient_name': obj.delivery_address.recipient_name,
                'address_line1': obj.delivery_address.address_line1,
                'city': obj.delivery_address.city,
                'region': obj.delivery_address.region
            }
        return None

class DeliveryAddressSerializer(serializers.ModelSerializer):
    """
    配送地址序列化器
    Delivery address serializer
    """
    class Meta:
        model = DeliveryAddress
        fields = '__all__'