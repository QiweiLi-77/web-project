from django.db import models
from django.core.validators import MinValueValidator
from django.utils.html import format_html


class Types(models.Model):
    """
    Product type model, containing first and second level categories
    """
    id = models.AutoField(primary_key=True)
    firsts = models.CharField('First-level Category', max_length=100)
    seconds = models.CharField('Second-level Category', max_length=100)

    def __str__(self):
        return f"{self.firsts} - {self.seconds}"

    class Meta:
        verbose_name = 'Product Type'
        verbose_name_plural = 'Product Types'
        unique_together = ('firsts', 'seconds')


class CommodityInfos(models.Model):
    """
    Product information model - with foreign key to Types table
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField('Product Name', max_length=100)
    product_type = models.ForeignKey(
        Types,
        on_delete=models.PROTECT,
        verbose_name='Product Type',
        related_name='products'
    )
    base_price = models.DecimalField('Price', max_digits=10, decimal_places=2)
    stock = models.IntegerField('Stock', default=0)
    sold = models.IntegerField('Sold Quantity', default=0)
    likes = models.IntegerField('Collection Count')
    created = models.DateField('Launch Date', auto_now_add=True)
    img = models.FileField('Main Image', upload_to='imgs')
    details = models.FileField('Product Details', upload_to='details')

    def __str__(self):
        return str(self.name)

    @property
    def first_category(self):
        """Get first-level category"""
        return self.product_type.firsts if self.product_type else ""

    @property
    def second_category(self):
        """Get second-level category"""
        return self.product_type.seconds if self.product_type else ""

    @property
    def type_display(self):
        """Get full type display"""
        return str(self.product_type) if self.product_type else ""

    class Meta:
        verbose_name = 'Product Information'
        verbose_name_plural = 'Product Information'