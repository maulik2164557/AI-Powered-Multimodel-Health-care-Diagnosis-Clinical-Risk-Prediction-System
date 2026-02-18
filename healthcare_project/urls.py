from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The built-in Django Admin portal
    path('admin/', admin.site.index), # We use admin.site.index because the file is fresh
    
    # We will connect our 'core' app URLs here in the next step
    # path('', include('core.urls')), 
]

# This allows Django to serve medical images/scans during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)