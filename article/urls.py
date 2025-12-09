from django.urls import path
from . import views


urlpatterns = [
    path('', views.article_list_view, name='article_list'),
    path('like/<int:article_id>/', views.like_article_view, name='like_article'),
    path('category/<str:slug>/', views.category_article_list_view, name='category_articles'),
]
