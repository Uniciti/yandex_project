# power_stations/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500, handler403
from . import views

handler404 = 'power_stations.views.page_not_found'
handler500 = 'power_stations.views.server_error'
handler403 = 'power_stations.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('', include('substations.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('users/', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path('404/', views.page_not_found, {'exception': Exception()}),
        path('500/', views.server_error),
        path('403/', views.csrf_failure),
    ]