from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings

"""
主URL配置文件
Main URL configuration file

定义整个项目的URL路由结构，包括应用、静态资源和媒体文件的路径
Defines the URL routing structure for the entire project, including paths for applications, 
static resources, and media files
"""

urlpatterns = [
    # 管理后台路由
    # Admin site route
    path('admin/', admin.site.urls),

    # 商品应用API路由，包含在api/v1/commodity/前缀下
    # Commodity application API routes under the api/v1/commodity/ prefix
    path('api/v1/commodity/', include(('commodity.urls', 'commodity'), namespace='commodity')),

    # 购物者应用API路由，包含在api/v1/shopper/前缀下
    # Shopper application API routes under the api/v1/shopper/ prefix
    path('api/v1/shopper/', include(('shopper.urls', 'shopper'), namespace='shopper')),

    # 配置媒体资源的路由信息
    # Configure routes for media resources
    re_path('media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}, name='media'),

    # 定义静态资源的路由信息
    # Define routes for static resources
    re_path('static/(?P<path>.*)', serve, {'document_root': settings.STATIC_ROOT}, name='static'),
]