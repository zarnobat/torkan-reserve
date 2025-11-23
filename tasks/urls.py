# urls.py
from rest_framework.routers import DefaultRouter
from .views import TaskCategoryViewSet, TaskViewSet
from django.urls import path 
from . import views
router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="tasks")
router.register("categories", TaskCategoryViewSet, basename="categories")


urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('tasks/users/', views.user_list),

] + router.urls