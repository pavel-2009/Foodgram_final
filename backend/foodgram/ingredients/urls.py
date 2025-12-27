from django.urls import path

from . import views

urlpatterns = [
    path('', views.IngredientList.as_view(), name='ingredient-list'),
    path('<int:pk>/', views.IngredientDetail.as_view(),
         name='ingredient-detail'),
]
