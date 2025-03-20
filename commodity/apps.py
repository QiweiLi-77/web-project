from django.apps import AppConfig


class CommodityConfig(AppConfig):
    """
    商品应用配置类
    Commodity application configuration class
    """
    # 默认自动字段类型 / Default auto field type
    default_auto_field = 'django.db.models.BigAutoField'

    # 应用名称 / Application name
    name = 'commodity'

    # 后台显示名称 / Admin display name
    verbose_name = 'Product Management'  # Product Management