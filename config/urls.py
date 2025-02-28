from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings


from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    re_path(r'^i18n/', include('django.conf.urls.i18n')),

    path('admin/', admin.site.urls),

    path('store/', include('store.urls')),

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
