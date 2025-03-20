from pathlib import Path

"""
Django项目设置文件
Django project settings file

包含项目的所有配置选项，如数据库设置、安装的应用、中间件等
Contains all configuration options for the project such as database settings, 
installed applications, middleware, etc.
"""

# 在项目中构建路径，如: BASE_DIR / 'subdir'
# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent

# 安全警告: 在生产环境中保密密钥
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tq%piy+c3pntex*%)7m&1xoo1&1hb6cp2v42eyqaj)%f%jxc&5'

# 安全警告: 在生产环境中不要开启调试模式
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 允许的主机列表，'*'表示允许所有
# List of allowed hosts, '*' means allow all
ALLOWED_HOSTS = ['*']

# 已安装的应用列表
# List of installed applications
INSTALLED_APPS = [
    # Django核心应用
    # Django core applications
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 第三方应用
    # Third-party applications
    'rest_framework',
    'corsheaders',

    # 项目应用
    # Project applications
    'commodity',
    'shopper',
]

# 中间件配置
# Middleware configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 添加中间件LocaleMiddleware用于国际化
    # Add LocaleMiddleware for internationalization
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 根URL配置
# Root URL configuration
ROOT_URLCONF = 'server.urls'

# 模板配置
# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI应用配置
# WSGI application configuration
WSGI_APPLICATION = 'server.wsgi.application'

# 数据库配置
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'py_online_mall',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

# 密码验证器配置
# Password validation configuration
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# 国际化配置
# Internationalization configuration
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_TZ = True

# 静态文件和媒体文件配置
# Static files and media files configuration
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATIC_ROOT = BASE_DIR / 'static'

# 默认自动字段类型
# Default auto field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework配置
# REST Framework configuration
REST_FRAMEWORK = {
    # 配置分页器 / Configure paginator
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    # 每页的数据量 / Number of items per page
    'PAGE_SIZE': 6,
    # 用户认证方式 / User authentication methods
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

# 设置跨域访问
# Configure Cross-Origin Resource Sharing (CORS)

# 指定所有域名(IP)都可以访问，默认为False
# Allow all domains/IPs to access, default is False
CORS_ORIGIN_ALLOW_ALL = True

# 设置允许携带Cookie
# Allow cookies to be included in cross-site requests
CORS_ALLOW_CREDENTIALS = True

# 设置允许访问的域名(IP)
# Set allowed domains/IPs for access
# 如果CORS_ORIGIN_ALLOW_ALL=True则无需设置
# Not needed if CORS_ORIGIN_ALLOW_ALL=True
CORS_ORIGIN_WHITELIST = []

# 允许执行的请求方式
# Allowed request methods
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

# 允许执行的请求头
# Allowed request headers
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
)