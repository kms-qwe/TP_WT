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
   
   # Settings
   path('profile/edit', views.profile_edit, name='profile.edit')

]

