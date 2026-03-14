from django.contrib import admin
from app.models import Task, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "content", "is_done", "created_at", "deadline")
    list_filter = ("is_done", "created_at", "deadline", "tags")
    search_fields = ("content",)
    filter_horizontal = ("tags",)
