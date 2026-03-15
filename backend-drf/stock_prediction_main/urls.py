from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api import views as api_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/health/', api_views.health_check, name='health'),
    path('api/v1/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'api.views.custom_404'
