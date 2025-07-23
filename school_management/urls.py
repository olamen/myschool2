# school_management/urls.py
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf.urls import handler403
from students import views
from django.views.generic.base import RedirectView




urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Add this line
    path('', RedirectView.as_view(url=reverse_lazy('index'), permanent=False)), #or any other url you want to redirect to


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('students.urls')),  # Include routes from the students app
    #path('', TemplateView.as_view(template_name='index.html')),
    path('accounting/', include('accounting.urls')),
    path('auth/', include('Auth.urls')),
    path("notes/", include("notes.urls")),
    path("reporting/", include("reporting.urls")),
    path('403/', views.forbidden_view, name='403'),  # Optional
)

handler403 = 'students.views.forbidden_view'