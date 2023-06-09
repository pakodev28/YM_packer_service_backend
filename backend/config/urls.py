from django.contrib import admin
from django.urls import path, include

admin.site.site_header = 'Yandex market'
admin.site.index_title = 'Админ панель'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
