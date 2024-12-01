from django.contrib import admin

from .models import Classe, Composition, Grade, Devoir, Parent, Student, Subject, Teacher, AppConfig, SessionYearModel

# Register your models here.
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'due_date', 'score', 'get_weighted_score']

admin.site.register(Devoir, HomeworkAdmin)
admin.site.register(Student)
admin.site.register(Classe)
admin.site.register(Grade)
admin.site.register(Composition)
admin.site.register(AppConfig)
admin.site.register(SessionYearModel)



@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name','class_enrolled')
    ordering = ('class_enrolled',)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'get_children_names')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    filter_horizontal = ('children',)  # Enable easier management of linked students

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_subjects', 'salary', 'salary_type', 'is_active', 'enrollment_date')
    list_filter = ('salary_type', 'is_active')
    search_fields = ('name', 'subjects__name')

    def get_subjects(self, obj):
        return obj.get_subjects()
    get_subjects.short_description = "Subjects"