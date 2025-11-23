from django.db import models
from django.shortcuts import redirect, render
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet
from django.utils.text import slugify
from django.forms import CheckboxSelectMultiple


@register_snippet
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True,
                            verbose_name="نام دسته‌بندی")
    slug = models.SlugField(
        unique=True, verbose_name="اسلاگ", max_length=100, editable=False)

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    def save(self, **kwargs):
        self.slug = slugify(self.name)
        super().save(**kwargs)

    def __str__(self):
        return self.name


@register_snippet
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام تگ")

    panels = [
        FieldPanel("name"),
    ]

    class Meta:
        verbose_name = "تگ"
        verbose_name_plural = "تگ‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class ArticlePage(Page):
    intro = RichTextField(blank=True, verbose_name="خلاصه")
    body = RichTextField(verbose_name="متن مقاله")
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="تصویر اصلی"
    )

    category = models.ForeignKey(
        "Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="articles",
        verbose_name="دسته‌بندی"
    )

    tags = ParentalManyToManyField(
        "Tag",
        blank=True,
        related_name="articles",
        verbose_name="تگ‌ها"
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("category"),
        MultiFieldPanel([
            FieldPanel("tags", widget=CheckboxSelectMultiple,
                       disable_comments=True),
        ]
        ),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        from .forms import CommentForm
        context["form"] = CommentForm()
        context["comments"] = self.comments.filter(is_approved=True)
        context["latest_articles"] = (
            ArticlePage.objects.live().order_by("-first_published_at")[:3]
        )
        return context

    def serve(self, request):
        from .forms import CommentForm
        form = CommentForm()
        if request.method == "POST":
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.article = self
                comment.save()
                return redirect(self.url)
            else:
                form = CommentForm()

        context = self.get_context(request)
        return render(request, "article/article_page.html", context)


class ArticleLike(models.Model):
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, verbose_name="کاربر")
    article = models.ForeignKey(
        ArticlePage, on_delete=models.CASCADE, related_name="likes", verbose_name="مقاله")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        unique_together = ("user", "article")
        verbose_name = "لایک"
        verbose_name_plural = "لایک‌ها"

    def __str__(self):
        return f"{self.user} liked {self.article}"


@register_snippet
class Comment(models.Model):
    display_name = models.CharField(
        max_length=100, verbose_name="نام نمایشی", help_text="نامی که در کنار نظر نمایش داده می‌شود.")
    article = models.ForeignKey(
        ArticlePage, on_delete=models.CASCADE, related_name="comments", verbose_name="مقاله")
    content = models.TextField(verbose_name="متن نظر")
    is_approved = models.BooleanField(default=False, verbose_name="تأیید شده؟")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="تاریخ ارسال")

    panels = [
        FieldPanel("display_name", read_only=True),
        FieldPanel("content", read_only=True),
        FieldPanel("is_approved"),
        FieldPanel("created_at", read_only=True),
    ]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "نظر"
        verbose_name_plural = "نظرات"

    def __str__(self):
        return f"نظر {self.display_name} روی {self.article}"


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
