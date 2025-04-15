from django.urls import path
from recommendation_system import views

urlpatterns = [
    path("", views.home, name='home'),
    path('search/', views.search_view, name="search"),  
    path('inputs-recommendations/', views.input_recommendations_view, name='input_recommendations'),
]