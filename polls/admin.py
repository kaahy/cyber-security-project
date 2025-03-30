from django.contrib import admin
from .models import Choice, Question, Comment

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    fieldset1 = (None, {'fields': ['question_text']})
    fieldset2 = ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']})
    fieldsets = [fieldset1, fieldset2]
    inlines = [ChoiceInline, CommentInline]
    list_display = ('question_text', 'pub_date', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question_text']

admin.site.register(Question, QuestionAdmin)
