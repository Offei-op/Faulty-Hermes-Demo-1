from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'), # Add this
    path('', views.dashboard, name='home'),
    path('chat/<str:username>/', views.room, name='room'),
    path('add-friend/', views.add_friend, name='add_friend'),
    # We will add chat room and dashboard paths here next
]