from django.urls import path

from students import viewspages
from . import views

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashs/', viewspages.dashs, name='dashs'),  # Admins dashboard
    path('dashf/', viewspages.dashf, name='dashf'),  # Adminf dashboard
    path('dashboard/super_admin/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/professor/', views.professor_dashboard, name='professor_dashboard'),
    path('dashboard/parent_student/', views.parent_student_dashboard, name='parent_student_dashboard'),
]