from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('student/dashboard/', views.StudentDashboard, name='student_dashbaord'),
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
]
