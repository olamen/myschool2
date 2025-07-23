#Auth urls
from django.urls import path

from . import views
from . import views_api

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashs/', views.dashs, name='dashs'),  # Admins dashboard
    path('dashf/', views.dashf, name='dashf'),  # Adminf dashboard
    path('dashboard/super_admin/', views.super_admin_dashboard, name='super_admin_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/professor/', views.professor_dashboard, name='professor_dashboard'),
    path('dashp/', views.parent_student_dashboard, name='parent_student_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
        #page error url
    path('error/', views.error_page, name='error_page'),


    #api login
    path('api/login/', views_api.UserLoginView.as_view(), name='api_login'),
    path('api/logout/', views_api.UserLogoutView.as_view(), name='api_logout'),
    path('api/students/', views_api.StudentViewSet.as_view({'get':'list'}), name='api_students'),
    path('api/subjects/', views_api.SubjectListApiView.as_view(), name='api_subjects'),
    path('api/parents/', views_api.ParentListApiView.as_view(), name='api_parents'),
    path('api/test/', views_api.test_translation_view, name='test_translation'),
    #add homework
    #path('api/add_homework/', views_api.AddHomeworkView.as_view(), name='api_add_homework'),
    #add exam


]