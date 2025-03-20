from rest_framework import serializers
from .models import Types, CommodityInfos


class TypesSerializer(serializers.ModelSerializer):
    """
    Product type serializer
    """
    class Meta:
        model = Types
        fields = '__all__'


class CommodityInfosListSerializer(serializers.ModelSerializer):
    """
    Serializer for product listings, including basic info and price display
    """
    price_display = serializers.SerializerMethodField()

    class Meta:
        model = CommodityInfos
        fields = ['id', 'name', 'first_category', 'second_category', 'base_price', 'price_display', 'stock', 'sold', 'likes',
                  'created', 'img']

    def get_price_display(self, obj):
        """
        Get price display text
        """
        return f"£{obj.base_price}"


class CommodityInfosDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for product details
    """
    class Meta:
        model = CommodityInfos
        fields = '__all__'