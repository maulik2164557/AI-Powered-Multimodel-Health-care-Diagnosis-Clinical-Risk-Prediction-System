from django.contrib import admin
from django.urls import path, include # 'include' is necessary here
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This line connects the 'core' app's URLs to the main project
    path('', include('core.urls')), 
]

# Serving medical media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)