from django.urls import path
# 显式导入视图类和函数
from .views import commodityView, detailView, collectView

# 商品应用的URL路由配置
# URL routing configuration for commodity application
urlpatterns = [
    # 商品列表页路由 / Product listing page route
    path('list/', commodityView.as_view(), name='list'),

    # 商品详情页路由，包含商品ID参数 / Product detail page route with product ID parameter
    path('detail/<int:id>/', detailView.as_view(), name='detail'),

    # 商品收藏路由 / Product collection route
    path('collect/', collectView.as_view(), name='collect'),


]