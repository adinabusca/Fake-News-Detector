from django.urls import path
from . import views

urlpatterns =[
    path('', views.analyze_news, name = 'analyze_news'),
]
