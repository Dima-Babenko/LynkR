from django.contrib import admin
from django.urls import path, include
from accounts.views import home  # додаємо головну сторінку

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('admin/', admin.site.urls),
]
