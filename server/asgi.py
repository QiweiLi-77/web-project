import os

from django.core.asgi import get_asgi_application

"""
ASGI配置文件
ASGI configuration file

该文件包含ASGI应用程序的配置，用于部署Django应用程序
This file contains the ASGI application configuration used for deploying Django applications

ASGI (Asynchronous Server Gateway Interface) 支持异步功能，适用于WebSocket等
ASGI (Asynchronous Server Gateway Interface) supports asynchronous features, 
suitable for WebSocket and other protocols
"""

# 设置Django配置模块的环境变量
# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# 获取ASGI应用
# Get the ASGI application
application = get_asgi_application()