from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Reflection, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "is_curated",
        "created_at",
        "image_preview",
    )

    list_filter = ("is_curated", "created_at")
    search_fields = ("title", "content", "source")
    readonly_fields = ("created_at", "image_preview")

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:70px;border-radius:10px;" />',
                obj.image.url
            )
        return "—"


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author_display",
        "short_text",
        "is_anonymous",
        "created_at",
    )

    list_filter = ("is_anonymous", "created_at")
    search_fields = ("title", "text")
    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    def short_text(self, obj):
        return obj.text[:60] + "…" if len(obj.text) > 60 else obj.text
    short_text.short_description = "Preview"

    def author_display(self, obj):
        return "Anonymous" if obj.is_anonymous else obj.author.username
    author_display.short_description = "Author"

    
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("author", "short_content", "reflection", "created_at")
    search_fields = ("content",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    def short_content(self, obj):
        return obj.content[:50] + "…" if len(obj.content) > 50 else obj.content
    short_content.short_description = "Comment"
