from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from wagtail.fields import StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام تگ")
    slug = models.SlugField(unique=True, verbose_name="اسلاگ")

    class Meta:
        verbose_name = "تگ"
        verbose_name_plural = "تگ‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'پیش‌نویس'),
        ('published', 'انتشار'),
    )

    title = models.CharField(max_length=200, verbose_name="عنوان")
    slug = models.SlugField(unique=True, verbose_name="اسلاگ")
    author = models.ForeignKey("accounts.User", on_delete=models.CASCADE, verbose_name="نویسنده")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="articles", verbose_name="دسته‌بندی")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="تگ‌ها")
    content = RichTextUploadingField(verbose_name="محتوا")
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="وضعیت انتشار"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "مقاله"
        verbose_name_plural = "مقاله‌ها"

    def __str__(self):
        return self.title

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.filter(is_approved=True).count()


class ArticleLike(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, verbose_name="کاربر")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="likes", verbose_name="مقاله")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        unique_together = ("user", "article")
        verbose_name = "لایک"
        verbose_name_plural = "لایک‌ها"

    def __str__(self):
        return f"{self.user} liked {self.article}"


class Comment(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, verbose_name="کاربر")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments", verbose_name="مقاله")
    content = models.TextField(verbose_name="متن نظر")
    is_approved = models.BooleanField(default=True, verbose_name="تأیید شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ارسال")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"

    def __str__(self):
        return f"نظر {self.user} روی {self.article}"
    

# Gallery

class GalleryImage(Orderable):
    page = ParentalKey(
        "GalleryPage",
        on_delete=models.CASCADE,
        related_name="gallery_images"
    )
    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        related_name="+",
    )
    caption = models.CharField(
        max_length=250, blank=True, verbose_name="عنوان تصویر")
    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]


class GalleryPage(Page):
    description = models.TextField(blank=True, verbose_name="توضیحات گالری")

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        InlinePanel("gallery_images", label="تصاویر گالری"),
    ]
