from django.contrib import admin
from .models import *
from jalali_date import date2jalali
from config.admin_site import custom_admin_site

@admin.register(Category, site=custom_admin_site)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag, site=custom_admin_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article, site=custom_admin_site)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "status", "likes_count", "comments_count", "shamsi_date")
    list_filter = ("status", "created_at", "author", "category", "tags")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    ordering = ["-created_at"]
    exclude = ("author",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # یعنی مقاله جدید داره ساخته میشه
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='تاریخ ایجاد')
    def shamsi_date(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')


@admin.register(ArticleLike, site=custom_admin_site)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "shamsi_date")
    exclude = ("user",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        return super().save_model(request, obj, form, change)

    @admin.display(description='تاریخ ایجاد')
    def shamsi_date(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')

@admin.register(Comment, site=custom_admin_site)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "article", "is_approved", "shamsi_date")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content",)
    exclude = ("user",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:  
            obj.user = request.user
        super().save_model(request, obj, form, change)

    @admin.display(description='تاریخ ایجاد')
    def shamsi_date(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')


@admin.register(Gallery, site=custom_admin_site)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title' , 'status' , 'shamsi_date']
    list_filter = ['status' , 'created_at']

    @admin.display(description='تاریخ ایجاد')
    def shamsi_date(self,obj):
        return date2jalali(obj.created_at).strftime('%Y/%m/%d')