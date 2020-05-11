from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from StudentSupport import views

urlpatterns = [
    # Home Page and Authentication urls > Start
    path('', views.HomePageView, name='home'),
    path('courtesy/', views.Courtesy, name='courtesy'),
    path('contact-us/', views.ContactUs, name='contact_us'),
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
    path('principal/feedback-section/<int:dept_id>/<str:type>/', views.Principal_FeedbackSection, name='principal_feedback_section'),

    # Below 2 views are for viewing feedback of assigned subject to hod
    path('principal/view-detailed-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.Principal_SubjectDetailedFeedback, name='principal_subject_detailed_feedback'),
    path('principal/view-average-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.Principal_SubjectAverageFeedback, name='principal_subject_average_feedback'),
    path('principal/subjectwise-average-feedback/<str:type>/<int:dept_id>/', views.PrincipalSubjectwiseAverageFeedback, name='principal_subjectwise_average_feedback'),
    path('change-hod/', views.EditHOD, name='change_hod'),
    # Principal Related urls > End

    # HOD Related urls > Start
    path('hod/dashboard/', views.HodDashboard, name='hod_dashboard'),
    path('hod/profile/', views.HOD_Profile_View, name='hod_profile'),
    path('hod/manage-department/', views.HOD_Manage_department, name='hod_manage_department'),
    path('hod/manage-news/', views.HODManageNews, name='hod_manage_news'),
    path('remove-faculty/', views.RemoveFaculty_AJAX, name='remove_faculty'),
    path('modify-subjects/', views.Modify_Subject_AJAX, name='ajax_modify_subject'),

    # this subject wise view will also be used in principal side.
    path('hod/subjectwise-average-feedback/<str:type>/<int:dept_id>/', views.HODSubjectwiseAverageFeedback, name='hod_subjectwise_average_feedback'),

    # Below 2 views are for viewing feedback of assigned subject to hod
    path('hod/view-detailed-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.HOD_SubjectDetailedFeedback, name='hod_subject_detailed_feedback'),
    path('hod/view-average-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.HOD_SubjectAverageFeedback, name='hod_subject_average_feedback'),

    # Below view is for viewing feedback for all faculties
    path('hod/feedback-section/<int:dept_id>/<str:type>/', views.HOD_FeedbackSection, name='hod_feedback_section'),
    # HOD Related urls > End

    # Faculty Related urls > Start
    path('faculty/dashboard/', views.FacultyDashboard, name='faculty_dashboard'),
    path('faculty/profile/', views.FacultyProfile, name='faculty_profile'),
    path('faculty/assigned-subjects/', views.FacultyAssignedSubjects, name='faculty_assigned_subjects'),
    path('faculty/manage-news/', views.FacultyManageNews, name='faculty_manage_news'),
    path('faculty/view-detailed-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.Faculty_SubjectDetailedFeedback, name='faculty_subject_detailed_feedback'),
    path('faculty/view-average-feedback/<str:type>/<str:sub_id>/<int:fac_id>/', views.Faculty_SubjectAverageFeedback, name='faculty_subject_average_feedback'),
    # Faculty Related urls > End

    # Student Related urls > Start
    path('student/dashboard/', views.StudentDashboard, name='student_dashboard'),
    path('student/feedback-section/<str:type>/', views.StudentFeedbackSection, name='student_feedback_section'),
    path('student/complaint-section/', views.StudentComplaintSectionView, name='student_complaint_section'),
    path('get-feedback/', views.GetFeedback, name='GetFeedback'),
    path('student/profile/', views.StudentProfile, name='student_profile'),
    # Student Related urls > End

    # Committee Related urls > Start
    path('committee/chairperson/dashboard/<int:com_id>/', views.CommitteeChairpersonDashboard, name='chaiperson_dashboard'),
    path('committee/chairperson/members/<int:com_id>/', views.CommitteeManageMembers, name='manage_members'),
    path('committee/dashboard/<int:com_id>/', views.CommitteeMemberDashboard, name='member_dashboard'),
    path('committee/members/<int:com_id>/', views.CommitteeViewMembers, name='view_members'),
    # Committee Related urls > End

    # Feedback Ajax Endpoints url > Start
    path('get-subjectwise-average-feedback/', views.GetSubjectwiseAverageFeedback, name='get_subjectwise_average_feedback'),
    # Feedback Ajax Endpoints url > End
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)