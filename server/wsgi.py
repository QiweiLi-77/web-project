import os

from django.core.wsgi import get_wsgi_application

"""
WSGI配置文件
WSGI configuration file

该文件包含WSGI应用程序的配置，用于部署Django应用程序
This file contains the WSGI application configuration used for deploying Django applications
"""

# 设置Django配置模块的环境变量
# Set the environment variable for Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

# 获取WSGI应用
# Get the WSGI application
application = get_wsgi_application()