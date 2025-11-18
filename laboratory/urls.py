from django.urls import path
from . import views

urlpatterns = [
    path('result', views.view_lab_result, name='result'),

]
