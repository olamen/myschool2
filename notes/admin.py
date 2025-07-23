from django.contrib import admin

from .models import NoteComposition, Quiz, Question, Answer, Result



admin.site.register(NoteComposition)
admin.site.register(Quiz)

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score', 'date_taken')
    search_fields = ('student__username', 'quiz__name')
    list_filter = ('quiz',)
    verbose_name_plural = "QuizResults"


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1
    max_num = 10
    min_num = 1

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'quiz', 'created')
    search_fields = ('text',)
    list_filter = ('quiz',)
    inlines = [AnswerInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('quiz')
    
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)