# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # DASHBOARD HOME (Halaman Utama Setelah Login)
    path('', views.dashboard_view, name='dashboard'),

    # AUTH
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # FEATURES
    path('grammar/', views.grammar_view, name='grammar'),
    path('chat/', views.chat_view, name='chat'),
    path('chat/clear/', views.clear_chat_view, name='clear_chat'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('progress/', views.progress_view, name='progress'),
    path('progress/reset/', views.reset_progress_view, name='reset_progress'),
]