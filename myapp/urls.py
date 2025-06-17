from django.urls import path
from django.shortcuts import render

from . import views

#python manage.py runserver
#http://localhost:8000/myapp/

app_name = "myapp"

urlpatterns = [
    # # ex: /polls/
    # path("", views.index, name="index"),
    # ex: /polls/5/
    # path("<int:question_id>/", views.detail, name="detail"),
    # # ex: /polls/5/results/
    # path("<int:question_id>/results/", views.results, name="results"),
    # # ex: /polls/5/vote/
    # path("<int:question_id>/vote/", views.vote, name="vote"),
    ##ex: /myapp/
    path('', views.quiz_view, name='quiz_index'),
    path("<int:question_id>/", views.quiz_view, name="quiz"),
    path('submit/', views.quiz_submit, name='submit_choice'),
    path('completed/', views.quiz_thanks, name='quiz_thanks'),
    path('machine_learning/', views.ML_view, name='machine_learning'),
    path('about/', views.about_view, name='about')
]