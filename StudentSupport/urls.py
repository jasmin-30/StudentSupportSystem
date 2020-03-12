from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('student/dashboard/', views.StudentDashboard, name='student_dashbaord'),
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('committee/dashboard/', views.CommitteeDashboard, name='committee_dashboard'),
    path('faculty/viewdetailedfeedback/', views.FacultyViewDetailedFeedback, name='view_detailed_feedback'),
    path('faculty/viewaveragefeedback/', views.FacultyViewAverageFeedback, name='view_average_feedback'),
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/viewdetailedfeedback/', views.HodViewDetailedFeedback, name='hod_view_detailed_feedback'),
    path('hod/viewaveragefeedback/', views.HodViewAverageFeedback, name='hod_view_average_feedback'),
]
