from django.urls import path
from . import views


urlpatterns = [
    # Главная страница и списки вопросов
    path('', views.home, name='home'),
    path('hot/', views.hot, name='hot_questions'),
    path('tag/<str:tag_name>/', views.tag, name='tag_questions'),
    
    # Работа с вопросами
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='new_question'),
    # Аутентификация
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('like/question/', views.like_question, name='like.question'),
    path('like/answer/', views.like_answer, name='like.answer'),
    path('answer/update/', views.update_answer, name='answer.update'),


   # Settings
    path('profile/edit', views.profile_edit, name='profile.edit'),
    path('search/', views.search_questions, name='search_questions')



]

