from django.contrib import admin

from .models import Class, Homework, Parent, Student

# Register your models here.
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'due_date', 'score', 'get_weighted_score']

admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Student)
admin.site.register(Class)

@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'get_children_names')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    filter_horizontal = ('children',)  # Enable easier management of linked students