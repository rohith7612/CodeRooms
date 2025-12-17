from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_room, name='create_room'),
    path('signup/', views.signup, name='signup'),
    path('room/<str:room_id>/', views.room_lobby, name='room_lobby'),
    path('room/<str:room_id>/arena/', views.arena, name='arena'),
    path('room/<str:room_id>/over/', views.game_over, name='game_over'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
