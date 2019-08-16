from django.urls import path
from . import views


urlpatterns = [
    path('', views.improve_home, name='improve-home'),
    path('venter-video/', views.venter_video, name='venter-video'),
    path('chart/', views.chart, name='chart'),
]
