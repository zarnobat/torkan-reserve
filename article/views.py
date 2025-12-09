from django.shortcuts import render, get_object_or_404
from .models import ArticlePage, ArticleLike, Category
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Count, Q
from .context_mixins import ArticleExtraContextMixin


def article_list_view(request):
    extra = ArticleExtraContextMixin().get_extra_context()

    articles = (
        ArticlePage.objects.live()
        .annotate(approved_comments_count=Count("comments", filter=Q(comments__is_approved=True)))
        .order_by("-first_published_at")
    )

    context = {"articles": articles}
    context.update(extra)

    return render(request, "article/article_list.html", context)


def category_article_list_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    extra = ArticleExtraContextMixin().get_extra_context()

    articles = (
        ArticlePage.objects.live()
        .filter(category=category)
        .annotate(approved_comments_count=Count("comments", filter=Q(comments__is_approved=True)))
        .order_by("-first_published_at")
    )

    context = {"articles": articles, "category": category}
    context.update(extra)

    return render(request, "article/article_list.html", context)


@require_POST
def like_article_view(request, article_id):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "Authentication required."}, status=403)

    article = get_object_or_404(ArticlePage, id=article_id)

    like_object, created = ArticleLike.objects.get_or_create(
        user=user, article=article)

    if not created:
        like_object.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({"liked": liked, "likes_count": article.likes.count()})
