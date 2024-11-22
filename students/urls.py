# students/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from students import views_teacher

from .views_class import class_archive, class_archived_list, class_list, class_create, class_update 

from .views_parent import parent_create, parent_detail, parent_list

from .views2 import BulkUploadStudentsView, GenerateExcelTemplateView, ListStudentPDFView
from .views import AppConfigViewSet, CompositionViewSet, HomeworkViewSet, IndexViewSet, StudentViewSet, SubjectViewSet, TeacherViewSet, ClassViewSet, SessionYearViewSet, AttendanceViewSet

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
    #path('', include(router.urls)),
    path('', IndexViewSet.as_view({'get': 'index'}), name='index'),
    path('students/student_list/', StudentViewSet.as_view({'get': 'student_list'}), name='students_list'),
    path('students/add/', StudentViewSet.as_view({'get': 'add_student', 'post': 'add_student'}), name='add_student'),
    path('students/student/<int:pk>/', StudentViewSet.as_view({'get': 'student_detail'}), name='student_detail'),
    path('students/download_template/', GenerateExcelTemplateView.as_view(), name='generate_excel_template'),
    path('students/bulk_upload/', BulkUploadStudentsView.as_view(), name='bulk_upload_students'),
    path('export/students_pdf/', ListStudentPDFView.as_view(), name='students_pdf'),


    path('classes/', class_list, name='class_list'),
    path('classes/create/', class_create, name='class_create'),
    path('classes/update/<int:class_id>/', class_update, name='class_update'),
    path('classes/archive/<int:class_id>/', class_archive, name='class_archive'),
    path('classes/archived/', class_archived_list, name='class_archived_list'),


    path('teachers/', views_teacher.teacher_list, name='teacher_list'),
    path('teachers/create/', views_teacher.teacher_create, name='teacher_create'),
    path('teachers/<int:pk>/update/', views_teacher.teacher_update, name='teacher_update'),
    path('teachers/<int:pk>/archive/', views_teacher.teacher_archive, name='teacher_archive'),
    path('teachers/archived/', views_teacher.teacher_archived_list, name='teacher_archived_list'),
    path('teachers/<int:pk>/restore/', views_teacher.teacher_restore, name='teacher_restore'),


    path('parents/', parent_list, name='parent_list'),
    path('parents/add/', parent_create, name='add_parent'),
    path('parents/<int:parent_id>/', parent_detail, name='parent_detail'),

    path('subjects/<int:pk>/subject_detail/', SubjectViewSet.as_view({'get': 'subject_detail'}), name='subject-detail'),
    path('subjects/subject_list/', SubjectViewSet.as_view({'get': 'subject_list'}), name='subject-list'),
    path('subjects/<int:pk>/subject_detail/', SubjectViewSet.as_view({'get': 'subject_detail'}), name='subject-detail'),
]