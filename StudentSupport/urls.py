from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('student/dashboard/', views.StudentDashboard, name='student_dashbaord'),
]