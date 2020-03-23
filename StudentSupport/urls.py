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
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('committee/dashboard/', views.CommitteeDashboard, name='committee_dashboard'),
    path('faculty/viewdetailedfeedback/', views.FacultyViewDetailedFeedback, name='view_detailed_feedback'),
    path('faculty/viewaveragefeedback/', views.FacultyViewAverageFeedback, name='view_average_feedback'),
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/viewdetailedfeedback/', views.HodViewDetailedFeedback, name='hod_view_detailed_feedback'),
    path('hod/viewaveragefeedback/', views.HodViewAverageFeedback, name='hod_view_average_feedback'),
    path('principal/dashboard/', views.PrincipalDashboard, name='principal_dashboard'),
    path('principal/department/', views.Department, name='department'),
    path('student/dashboard/student_profile', views.StudentProfile, name='student_profile'),
    path('faculty/dashboard/faculty_profile', views.FacultyProfile, name='faculty_profile'),
]
