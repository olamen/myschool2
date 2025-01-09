# students/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from students import views_subject, views_teacher
from students.views_devoir import composition_create, composition_delete, composition_list, composition_update, devoir_create, devoir_delete, devoir_list, devoir_update
from students.views_trimestres import trimestre_create, trimestre_delete, trimestre_list, trimestre_update

from .views_class import class_archive, class_archived_list, class_list, class_create, class_update 
from .views_composition import exam_detail, edit_exam
from .views_parent import parent_create, parent_detail, parent_list

from .views2 import BulkUploadStudentsView, GenerateExcelTemplateView, ListStudentPDFView
from .views import AppConfigViewSet, StudentViewSet, SubjectViewSet, TeacherViewSet, ClassViewSet, SessionYearViewSet, AttendanceViewSet, indexview, student_fees_by_month,update_student, get_classes, grades_list, add_grade, update_grade

router = DefaultRouter()
router.register(r'session-years', SessionYearViewSet)
router.register(r'students', StudentViewSet)
router.register(r'teachers', TeacherViewSet)
router.register(r'classes', ClassViewSet)
router.register(r'subject', SubjectViewSet)
router.register(r'attendances', AttendanceViewSet)
router.register(r'config', AppConfigViewSet)


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
    path('student-fees-by-month/', student_fees_by_month, name='student_fees_by_month'),


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
    path('parentscard/', parent_list, name='parent_list_card'),

    path('parents/add/', parent_create, name='add_parent'),
    path('parents/<int:parent_id>/', parent_detail, name='parent_detail'),
    
#subject
    path('subjects/', views_subject.subject_list, name='subject_list'),
    path('subjects/new/', views_subject.subject_form, name='subject_create'),
    path('subjects/<int:subject_id>/edit/', views_subject.subject_form, name='subject_update'),
    path('subjects/<int:subject_id>/toggle-status/', views_subject.subject_toggle_status, name='subject_toggle_status'),


    path("exams/<int:exam_id>/", exam_detail, name="exam_detail"),
    path("exams/<int:exam_id>/edit/", edit_exam, name="edit_exam"),

#
    path('trimestres/', trimestre_list, name='trimestre_list'),
    path('trimestres/create/', trimestre_create, name='trimestre_create'),
    path('trimestres/<int:pk>/update/', trimestre_update, name='trimestre_update'),
    path('trimestres/<int:pk>/delete/', trimestre_delete, name='trimestre_delete'),

    path('devoirs/', devoir_list, name='devoir_list'),
    path('devoirs/create/', devoir_create, name='devoir_create'),
    path('devoirs/<int:pk>/update/', devoir_update, name='devoir_update'),
    path('devoirs/<int:pk>/delete/', devoir_delete, name='devoir_delete'),

    path('compositions/', composition_list, name='composition_list'),
    path('compositions/create/', composition_create, name='composition_create'),
    path('compositions/<int:pk>/update/', composition_update, name='composition_update'),
    path('compositions/<int:pk>/delete/', composition_delete, name='composition_delete'),
]