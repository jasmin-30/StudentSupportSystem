from django.urls import path
from StudentSupport import views

urlpatterns = [
    # Home Page and Authentication urls > Start
    path('', views.HomePageView, name='home'),
    path('register/', views.RegisterView, name='register'),
    path('changePassword/', views.ChangePasswordView, name='change_password'),
    path('activate/', views.ConfirmAccountView, name='activate'),
    path('logout/', views.LogoutView, name='logout'),
    # Home Page and Authentication urls > End

    # Principal Related urls > Start
    path('principal/dashboard/', views.PrincipalDashboard, name='principal_dashboard'),
    path('principal/manage-committees/', views.ManageCommitteesView, name='manage_committees'),
    path('principal/profile/', views.PrincipalProfile, name='principal_profile'),
    path('edit-delete-committees/', views.EditCommittees, name="edit_committees"), # Only Principal Can Edit Committee
    path('principal/manage-department/', views.ManageDepartmentView, name='manage_department'),
    path('principal/view-detailed-feedback/<int:id>/', views.DetailedFeedback, name='principal_detailed_feedback'),
    path('principal/view-average-feedback/<int:id>/', views.AverageFeedback, name='principal_detailed_feedback'),
    path('change-hod/', views.EditHOD, name='change_hod'),
    path('principal/download-detailed-report/', views.DownloadDetailedReport, name='principal_download_detailed_report'),
    path('principal/download-average-report/', views.DownloadAverageReport, name='principal_download_average_report'),
    # Principal Related urls > End

    # HOD Related urls > Start
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/profile/', views.HOD_Profile_View, name='hod_profile'),
    path('hod/manage-department/', views.HOD_Manage_department, name='hod_manage_department'),
    path('hod/manage-news/', views.HODManageNews, name='hod_manage_news'),
    path('remove-faculty/', views.RemoveFaculty_AJAX, name='remove_faculty'),
    path('modify-subjects/', views.Modify_Subject_AJAX, name='ajax_modify_subject'),
    path('hod/view-detailed-feedback/<str:type>/', views.HodViewDetailedFeedback, name='hod_view_detailed_feedback'),
    path('hod/view-average-feedback/<str:type>/', views.HodViewAverageFeedback, name='hod_view_average_feedback'),
    # HOD Related urls > End

    # Faculty Related urls > Start
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('faculty/profile/', views.FacultyProfile, name='faculty_profile'),
    path('faculty/assigned-subjects/', views.FacultyAssignedSubjects, name='faculty_assigned_subjects'),
    path('faculty/manage-news/', views.FacultyManageNews, name='faculty_manage_news'),
    path('faculty/view-detailed-feedback/<str:type>/', views.FacultyViewDetailedFeedback, name='faculty_view_detailed_feedback'),
    path('faculty/view-average-feedback/<str:type>/', views.FacultyViewAverageFeedback, name='faculty_view_average_feedback'),
    # Faculty Related urls > End

    # Student Related urls > Start
    path('student/dashboard/', views.StudentDashboard, name='student_dashboard'),
    path('student/feedback-section/<str:type>/', views.StudentFeedbackSection, name='student_feedback_section'),
    path('student/complaint-section/', views.StudentComplaintSectionView, name='student_complaint_section'),
    path('get-feedback/', views.GetFeedback, name='GetFeedback'),
    path('student/profile/', views.StudentProfile, name='student_profile'),
    # Student Related urls > End

    # Committee Related urls > Start
    # path('committee/<str:committee>/', views.CommitteeDashboard, name='committee_dashboard'),
    path('committee/chairperson/dashboard/<int:com_id>/', views.CommitteeChairpersonDashboard, name='chaiperson_dashboard'),
    path('committee/chairperson/members/<int:com_id>/', views.CommitteeManageMembers, name='manage_members'),
    path('committee/dashboard/<int:com_id>/', views.CommitteeMemberDashboard, name='member_dashboard'),
    path('committee/members/<int:com_id>/', views.CommitteeViewMembers, name='view_members'),
    # Committee Related urls > End

    # Feedback Ajax Endpoints url > Start
    path('get-average-feedback/', views.GetAverageFeedback, name='get_average_feedback'),
    path('get-all-feedback/', views.GetAllFeedback, name='get_all_feedback'),
    # Feedback Ajax Endpoints url > End

    # Download Report > Start
    path('download/detailed-feedback/<str:type>/', views.DownloadDetailedFeedback, name='download_detailed_feedback'),
    path('download/average-feedback/<str:type>/', views.DownloadAverageFeedback, name='download_average_feedback'),
    # Download Report > End

]
