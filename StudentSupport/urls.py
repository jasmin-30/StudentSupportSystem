from django.urls import path
from StudentSupport import views

urlpatterns = [
    path('', views.HomePageView, name='home'),
    path('editable-table/', views.EditableTableView, name='editable-table'),
    path('register/', views.RegisterView, name='register'),
    path('changePassword/', views.ChangePasswordView, name='change_password'),
    path('student/dashboard/', views.StudentDashboard, name='student_dashboard'),
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('principal/dashboard/', views.PrincipalDashboard, name='principal_dashboard'),
    path('principal/manage-committees/', views.ManageCommitteesView, name='manage_committees'),
    path('edit-delete-committees/', views.EditCommittees, name="edit_committees"),
    path('principal/manage-department/', views.ManageDepartmentView, name='manage_department'),
    path('activate/', views.ConfirmAccountView, name='activate'),
    path('logout/', views.LogoutView, name='logout'),
    # path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('committee/dashboard/', views.CommitteeDashboard, name='committee_dashboard'),
    path('faculty/viewdetailedfeedback/', views.FacultyViewDetailedFeedback, name='view_detailed_feedback'),
    path('faculty/viewaveragefeedback/', views.FacultyViewAverageFeedback, name='view_average_feedback'),
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/viewdetailedfeedback/', views.HodViewDetailedFeedback, name='hod_view_detailed_feedback'),
    path('hod/viewaveragefeedback/', views.HodViewAverageFeedback, name='hod_view_average_feedback'),
    # path('principal/dashboard/', views.PrincipalDashboard, name='principal_dashboard'),
    path('student/dashboard/student_profile', views.StudentProfile, name='student_profile'),
    path('student/mid-sem-feedback/', views.StudentMidSemFeedbackView, name='student_mid_sem_feedback'),
    path('faculty/dashboard/faculty_profile', views.FacultyProfile, name='faculty_profile'),
]
