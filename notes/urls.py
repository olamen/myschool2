from django.urls import path
from .views import *

urlpatterns = [
    path("exams/", exam_list, name="exam_list"),
    # Homework URLs
    path('notedevoir/add/', ajouter_notes_devoir, name='add_note_devoir'),
    path('homeworks/', homework_list, name='homework_list'),
    path('homeworks/add/', add_homework, name='add_homework'),
    path('homeworks/edit/<int:pk>/', edit_homework, name='edit_homework'),
    path('homeworks/delete/<int:pk>/', delete_homework, name='delete_homework'),

    # Composition URLs
    path('compositions/', composition_list, name='note_composition'),
    path('compositions/add/', add_composition, name='add_note_composition'),
    path('compositions/edit/<int:pk>/', edit_composition, name='edit_note_composition'),
    path('compositions/delete/<int:pk>/', delete_composition, name='delete_note_composition'),

    path('get_students/<int:classe_id>/<int:devoir_id>/', get_students, name='get_students'),
    path('notes_devoir/save/', save_note_devoir, name='save_note'),
]