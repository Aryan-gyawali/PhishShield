# phishshield/urls.py
from django.urls import path
from simulator import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test/', views.test, name='test'),
    path('report/', views.report, name='report'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('', views.dashboard),  # Default to dashboard
]