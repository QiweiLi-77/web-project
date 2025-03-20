from django.db import models
from commodity.models import CommodityInfos
from django.contrib.auth.models import User

# Order status choices tuple
ORDER_STATUS = (
    ('pending_payment', 'Pending Payment'),
    ('paid', 'Paid'),
    ('shipping', 'Shipping'),
    ('delivered', 'Delivered'),
    ('returning', 'Returning'),
)


class DeliveryAddress(models.Model):
    """
    Delivery address model to store customer shipping information.
    """
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField('User ID')  # ID of the user who owns this address
    recipient_name = models.CharField('Recipient Name', max_length=100)
    phone_number = models.CharField('Phone Number', max_length=20)
    address_line1 = models.CharField('Address Line 1', max_length=200)
    address_line2 = models.CharField('Address Line 2', max_length=200, blank=True, null=True)
    city = models.CharField('City', max_length=100)
    region = models.CharField('Region/State', max_length=100)
    postal_code = models.CharField('Postal Code', max_length=20)
    country = models.CharField('Country', max_length=100, default='United Kingdom')
    is_default = models.BooleanField('Default Address', default=False)

    def __str__(self):
        return f"{self.recipient_name}, {self.city}"

    class Meta:
        verbose_name = 'Delivery Address'
        verbose_name_plural = 'Delivery Addresses'


class CartInfos(models.Model):
    """
    Cart model to store items added to shopping cart by users.
    Tracks quantity and links to both product and user.
    """
    id = models.AutoField(primary_key=True)
    quantity = models.IntegerField('Quantity')  # Amount of product being purchased
    # Foreign key to product information, with null allowed if product is deleted
    commodityInfos_id = models.ForeignKey(
        CommodityInfos,
        on_delete=models.SET_NULL,
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name='Product'
    )
    user_id = models.IntegerField('User ID')  # ID of the user who owns this cart item

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'


class OrderInfos(models.Model):
    """
    Order model to store information about customer orders.
    Tracks total price, creation date, user, and status.
    """
    id = models.AutoField(primary_key=True)
    price = models.FloatField('Total Price')  # Total price of the order
    created = models.DateTimeField('Creation Date', auto_now_add=True)  # 修改为 DateTimeField
    user_id = models.IntegerField('User ID')  # ID of the user who placed this order
    state = models.CharField(
        'Order Status',
        max_length=20,
        choices=ORDER_STATUS,
        default='pending_payment'
    )  # Current status of the order

    # Stripe payment fields
    payment_id = models.CharField('Payment ID', max_length=100, blank=True, null=True)  # Stripe payment intent ID
    payment_method = models.CharField('Payment Method', max_length=20, default='stripe')  # Payment method used

    # Delivery address association
    delivery_address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Delivery Address',
        db_column='delivery_address_id'
    )

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'


class OrderItem(models.Model):
    """
    Order item model to store products in orders
    """
    order = models.ForeignKey(OrderInfos, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField('Product ID')
    product_name = models.CharField('Product Name', max_length=200)
    price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    quantity = models.IntegerField('Quantity')

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'


class CollectInfos(models.Model):
    """
    商品收藏信息模型
    """
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    commodityInfos_id = models.ForeignKey(CommodityInfos, on_delete=models.CASCADE, verbose_name='Product')
    created = models.DateTimeField('Creation Time', auto_now_add=True)

    class Meta:
        verbose_name = 'Collection'
        verbose_name_plural = 'Collections'
        # 确保用户不能重复收藏同一个商品
        unique_together = ('user_id', 'commodityInfos_id')

    def __str__(self):
        return f"{self.user_id.username} - {self.commodityInfos_id.name}"