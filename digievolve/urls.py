from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('courses/', include('courses.urls')),
    path('accounts/', include('accounts.urls')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('resources/', include('resources.urls', namespace='resources')),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)