from django.contrib import admin

from .models import Classe, Composition, Grade, Devoir, Parent, Student, Subject, Teacher, AppConfig, SessionYearModel

# Register your models here.
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['name','trimestre','classe','subject', 'date', 'description', 'get_weighted_score']

admin.site.register(Devoir, HomeworkAdmin)
admin.site.register(Student)
admin.site.register(Classe)
admin.site.register(Grade)
admin.site.register(Composition)
admin.site.register(AppConfig)
admin.site.register(SessionYearModel)



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
    list_display = ('name', 'nni', 'salary', 'salary_type', 'enrollment_date', 'is_active', 'telephone', 'get_subjects')
    list_filter = ('salary_type', 'is_active')
    search_fields = ('name', 'nni', 'telephone')
    ordering = ('name',)

    def get_subjects(self, obj):
        return ", ".join([subject.name for subject in obj.subject.all()])
    get_subjects.short_description = 'Subjects'

    def search_by_subject(self, queryset, name, value):
        return queryset.filter(subject__name__icontains=value)
    
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if search_term:
            queryset |= self.model.objects.filter(subject__name__icontains=search_term)
        return queryset, use_distinct
