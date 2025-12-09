
class ArticleExtraContextMixin:
    def get_extra_context(self):
        from .models import ArticlePage, Category, Tag
        return {
            "latest_articles": ArticlePage.objects.live().order_by("-first_published_at")[:3],
            "categories": Category.objects.all(),
            "tags": Tag.objects.all(),
        }
