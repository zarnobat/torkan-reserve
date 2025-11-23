from django.shortcuts import render
from .models import ArticlePage


def article_list_view(request):
    articles = ArticlePage.objects.live().order_by("-first_published_at")
    return render(request, "article/article_list.html", {"articles": articles})
