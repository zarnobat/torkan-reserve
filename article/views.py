from django.shortcuts import render
from .models import ArticlePage


def article_list_view(request):
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
