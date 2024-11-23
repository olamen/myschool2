# school_management/urls.py
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf.urls import handler403
from students import views



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('students.urls')),  # Include routes from the students app
    #path('', TemplateView.as_view(template_name='index.html')),
    path('accounting/', include('accounting.urls')),
    path('auth/', include('Auth.urls')),
    path('403/', views.forbidden_view, name='403'),  # Optional
    


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



handler403 = 'students.views.forbidden_view'