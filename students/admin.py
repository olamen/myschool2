from django.contrib import admin

from .models import Assignment, Classe, Composition, Grade, Devoir, Parent, Student, Subject, Teacher, AppConfig, SessionYearModel, TeacherSubject

# Register your models here.
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['name','trimestre', 'date', 'description', 'get_weighted_score']

admin.site.register(Devoir, HomeworkAdmin)
admin.site.register(Student)
admin.site.register(Classe)
admin.site.register(Grade)
admin.site.register(Composition)
admin.site.register(AppConfig)
admin.site.register(SessionYearModel)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'title', 'description', 'file', 'due_date']
    search_fields = ['classroom__name', 'title']
    list_filter = ['classroom', 'due_date']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'get_children_names')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    filter_horizontal = ('children',)  # Enable easier management of linked students


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'nni', 'salary', 'salary_type', 'enrollment_date', 'is_active', 'telephone', 'get_subjects','get_classes')
    list_filter = ('salary_type', 'is_active')
    search_fields = ('name', 'nni', 'telephone')
    ordering = ('name',)
    filter_horizontal = ('classes',)  # Enable easier management of linked classes and subjects

    def get_subjects(self, obj):
        return ", ".join([subject.name for subject in obj.subject.all()])
    get_subjects.short_description = 'Subjects'

    def get_classes(self, obj):
        return ", ".join([classe.name for classe in obj.classes.all()])
    get_classes.short_description = 'Classes'

    def search_by_subject(self, queryset, name, value):
        return queryset.filter(subject__name__icontains=value)
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(subject__name__icontains=search_term)
        return queryset, use_distinct

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject')  # Customize the display as needed