from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('changePassword/', views.ChangePasswordView, name='change_password'),
    path('student/dashboard/', views.StudentDashboard, name='student_dashbaord'),
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashbaord'),
    path('principal/dashboard/', views.PrincipalDashboard, name='principal_dashbaord'),
    path('activate/', views.ConfirmAccountView, name='activate'),
    path('logout/', views.LogoutView, name='logout'),
]
