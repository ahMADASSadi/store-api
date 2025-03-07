from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings


from drf_spectacular.views import (
    SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView)
from debug_toolbar.toolbar import debug_toolbar_urls


urlpatterns = [
    
    path("auth/", include("core.urls")),

    path('admin/', admin.site.urls),

    path('store/', include('store.urls')),

    re_path(r'^i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += [

        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

        path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'),
             name='swagger-ui'),

        path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()
