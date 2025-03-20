from django.apps import AppConfig


class ShopperConfig(AppConfig):
    """
    购物者应用配置类
    Shopper application configuration class
    """
    # 默认自动字段类型 / Default auto field type
    default_auto_field = 'django.db.models.BigAutoField'

    # 应用名称 / Application name
    name = 'shopper'

    # 后台显示名称 / Admin display name
    verbose_name = 'Order Management'  # Order Management