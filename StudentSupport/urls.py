from django.urls import path
from StudentSupport import views

urlpatterns = [
    # Home Page and Authentication urls > Start
    path('', views.HomePageView, name='home'),
    path('editable-table/', views.EditableTableView, name='editable-table'),
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
    path('departments/<str:dept>/', views.DepartmentsView, name='departments'),
    path('fetch-faculties/', views.FetchFaculties, name='fetch_faculties'),
    path('change-hod/', views.EditHOD, name='change_hod'),
    # Principal Related urls > End

    # HOD Related urls > Start
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/profile/', views.HOD_Profile_View, name='hod_profile'),
    path('hod/manage-department/', views.HOD_Manage_department, name='hod_manage_department'),
    path('remove-faculty/', views.RemoveFaculty_AJAX, name='remove_faculty'),
    path('modify-subjects/', views.Modify_Subject_AJAX, name='ajax_modify_subject'),
    path('hod/viewdetailedfeedback/', views.HodViewDetailedFeedback, name='hod_view_detailed_feedback'),
    path('hod/viewaveragefeedback/', views.HodViewAverageFeedback, name='hod_view_average_feedback'),
    # HOD Related urls > End

    # Faculty Related urls > Start
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('faculty/profile/', views.FacultyProfile, name='faculty_profile'),
    path('faculty/view-detailed-feedback/<str:type>/', views.FacultyViewDetailedFeedback, name='view_detailed_feedback'),
    path('faculty/view-average-feedback/<str:type>/', views.FacultyViewAverageFeedback, name='view_average_feedback'),
    # Faculty Related urls > End

    # Student Related urls > Start
    path('student/dashboard/', views.StudentDashboard, name='student_dashboard'),
    path('student/mid-sem-feedback/', views.StudentMidSemFeedbackView, name='student_mid_sem_feedback'),
    path('student/end-sem-feedback/', views.StudentEndSemFeedbackView, name='student_end_sem_feedback'),
    path('student/dashboard/complaint/', views.StudentComplaintSectionView, name='student_complaint_section'),
    path('getFacultyName/', views.getFacultyName, name='getFacultyName'),
    path('checkStatus/', views.checkStatus, name='checkStatus'),
    path('checkStatusforEndSem/', views.checkStatusforEndSem, name='checkStatusforEndSem'),
    path('getFeedback/', views.GetFeedback, name='GetFeedback'),
    path('getFeedbackforEndSem/', views.GetFeedbackForEndSem, name='GetFeedbackForEndSem'),
    path('student/dashboard/student_profile', views.StudentProfile, name='student_profile'),
    # Student Related urls > End

    # Committee Related urls > Start
    path('committee/<str:committee>/', views.CommitteeDashboard, name='committee_dashboard'),
    # Committee Related urls > End

]
