# phishshield/urls.py
from django.urls import path
from simulator import views
from django.views.generic import TemplateView


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('test/', views.test, name='test'),
    path('report/', views.report, name='report'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),  # Admin route
    path('manage_user/', views.manage_user, name='manage_user'),
    path('rankings/', views.rankings_view, name='rankings'),  # New endpoint for rankings
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('test/<str:folder_name>/<str:page_name>/', views.show_test_page, name='show_test_page'),
    path('', views.dashboard, name='home'),  # Default to dashboard
]
