from django.contrib import admin

from .models import Classe, Homework, Parent, Student, Teacher

# Register your models here.
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'due_date', 'score', 'get_weighted_score']

admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Student)
admin.site.register(Classe)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'get_children_names')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    filter_horizontal = ('children',)  # Enable easier management of linked students

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'salary', 'salary_type', 'is_active')
    list_filter = ('salary_type', 'is_active')
    search_fields = ('name', 'subject')
    ordering = ('name',)