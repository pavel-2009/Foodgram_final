from django.urls import path

from . import views

urlpatterns = [
    path('', views.TagList.as_view(), name='tag-list'),
    path('<int:pk>/', views.TagDetail.as_view(), name='tag-detail'),
]
