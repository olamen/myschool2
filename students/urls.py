# students/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from students import views_subject, views_teacher

from .views_class import class_archive, class_archived_list, class_list, class_create, class_update 

from .views_parent import parent_create, parent_detail, parent_list

from .views2 import BulkUploadStudentsView, GenerateExcelTemplateView, ListStudentPDFView
from .views import AppConfigViewSet, CompositionViewSet, HomeworkViewSet, StudentViewSet, SubjectViewSet, TeacherViewSet, ClassViewSet, SessionYearViewSet, AttendanceViewSet, indexview,update_student, get_classes, grades_list, add_grade, update_grade

router = DefaultRouter()
router.register(r'session-years', SessionYearViewSet)
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'subject', SubjectViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'config', AppConfigViewSet)
router.register(r'homeworks', HomeworkViewSet)
router.register(r'compositions', CompositionViewSet)

urlpatterns = [
    path('', indexview, name='index'),
    #path('', IndexViewSet.as_view({'get': 'index'}), name='index'),
    path('students/student_list/', StudentViewSet.as_view({'get': 'student_list'}), name='students_list'),
    path('students/add/', StudentViewSet.as_view({'get': 'add_student', 'post': 'add_student'}), name='add_student'),
    path('students/student/<int:pk>/', StudentViewSet.as_view({'get': 'student_detail'}), name='student_detail'),
    path('students/download_template/', GenerateExcelTemplateView.as_view(), name='generate_excel_template'),
    path('students/bulk_upload/', BulkUploadStudentsView.as_view(), name='bulk_upload_students'),
    path('export/students_pdf/', ListStudentPDFView.as_view(), name='students_pdf'),
    path('students/<int:student_id>/update/', update_student, name='update_student'),  # Update student


    path('grades/', grades_list, name='grades_list'),
    path('grades/add/', add_grade, name='add_grade'),
    path('grades/<int:grade_id>/update/', update_grade, name='update_grade'),
    
    path('classes/', class_list, name='class_list'),
    path('classes/create/', class_create, name='class_create'),
    path('classes/update/<int:class_id>/', class_update, name='class_update'),
    path('classes/archive/<int:class_id>/', class_archive, name='class_archive'),
    path('classes/archived/', class_archived_list, name='class_archived_list'),
    path('get-classes/<int:grade_id>/',get_classes, name='get_classes'),



    path('teachers/', views_teacher.teacher_list, name='teacher_list'),
    path('teachers/create/', views_teacher.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/update/', views_teacher.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/archive/', views_teacher.teacher_archive, name='teacher_archive'),
    path('teachers/archived/', views_teacher.teacher_archived_list, name='teacher_archived_list'),
    path('teachers/<int:pk>/restore/', views_teacher.teacher_restore, name='teacher_restore'),


    path('parents/', parent_list, name='parent_list'),
    path('parents/add/', parent_create, name='add_parent'),
    path('parents/<int:parent_id>/', parent_detail, name='parent_detail'),

    path('subjects/', views_subject.subject_list, name='subject_list'),
    path('subjects/create/', views_subject.subject_create, name='subject_create'),
    path('subjects/<int:subject_id>/update/', views_subject.subject_update, name='subject_update'),
    path('subjects/<int:subject_id>/toggle/', views_subject.subject_toggle_status, name='subject_toggle_status'),
]