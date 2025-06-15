from django.contrib import admin
from django.urls import path, include
from accounts.views import home
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('chat/', include('chat.urls')),
    path('admin/', admin.site.urls),
    path('groups/', include('groups.urls', namespace='groups')),
    path('notifications/', include('notifications.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)