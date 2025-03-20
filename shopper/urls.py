# shopper/urls.py - 完整的URL配置

from django.urls import path
from .views import *

urlpatterns = [
    # 用户认证路由
    path('login/', loginView.as_view(), name='login'),
    path('logout/', logoutView.as_view(), name='logout'),

    # 用户中心和购物车路由
    path('home/', shopperView.as_view(), name='home'),
    path('shopcart/', shopcartView.as_view(), name='shopcart'),

    # 支付路由
    path('pays/', paysView.as_view(), name='pays'),
    path('delete/', deleteView.as_view(), name='delete'),
    path('stripe-webhook/', stripeWebhookView.as_view(), name='stripe-webhook'),

    # 地址管理路由
    path('addresses/', AddressView.as_view(), name='addresses'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
    path('addresses/set-default/', DefaultAddressView.as_view(), name='set-default-address'),

    # 用户资料路由
    path('profile/', UserProfileView.as_view(), name='user-profile'),

    # 添加收藏相关的URL
    path('collect/', CollectView.as_view()),
]