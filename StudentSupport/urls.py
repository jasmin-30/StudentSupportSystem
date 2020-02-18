from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
]