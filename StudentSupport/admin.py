from django.contrib import admin
from django.contrib.auth import get_user_model
from .forms import UserAdminChangeForm, UserAdminCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *

User = get_user_model()

# Chagning Site header
admin.site.site_header = 'Student Support System Administration'
admin.site.site_title = 'Student Support System Admin'
# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin', 'active', 'timestamp')
    list_filter = ('admin', 'active', 'staff', 'role', 'timestamp')
    fieldsets = (
        ('Credentials', {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': (('admin', 'active', 'staff'),)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        ('Credentials', {
            'classes': ('wide',),
            'fields': (
                ('email', 'role'),
                ('password1', 'password2'),
                'active'
            )
        }
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


@admin.register(Principal)
class PrincipalAdmin(admin.ModelAdmin):
    list_display = ('name', 'auth_id')


def Mid_live(modeladmin, request, queryset):
    queryset.update(
        is_mid_sem_live=True
    )


Mid_live.short_description = 'Make Mid Semester Feedback live now'


def End_live(modeladmin, request, queryset):
    queryset.update(
        is_end_sem_live=True
    )


End_live.short_description = 'Make End Semester Feedback live now'


def Both_live(modeladmin, request, queryset):
    queryset.update(
        is_mid_sem_live=True,
        is_end_sem_live=True
    )


Both_live.short_description = 'Make Mid and End Semester Feedback live now'


def Mid_inactive(modeladmin, request, queryset):
    queryset.update(
        is_mid_sem_live=False
    )


Mid_inactive.short_description = 'Make Mid semester feedback inactive'


def End_inactive(modeladmin, request, queryset):
    queryset.update(
        is_end_sem_live=False
    )


End_inactive.short_description = 'Make End semester feedback inactive'


def Both_inactive(modeladmin, request, queryset):
    queryset.update(
        is_mid_sem_live=False,
        is_end_sem_live=False
    )


Both_inactive.short_description = 'Make Mid and End semester feedback inactive'


@admin.register(Departments)
class DepartmentAdmin(admin.ModelAdmin):
    actions = [Mid_live, End_live, Both_live, Mid_inactive, End_inactive, Both_inactive]
    list_display = ('dept_name', 'accronym', 'is_mid_sem_live', 'is_end_sem_live')
    list_filter = ('is_mid_sem_live', 'is_end_sem_live')
    ordering = ('dept_name',)


def Make_active(modeladmin, request, queryset):
    queryset.update(
        active=True
    )


Make_active.short_description = "Make Active"


def Make_inactive(modeladmin, request, queryset):
    queryset.update(
        active=False
    )


Make_inactive.short_description = "Make Inactive"


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    actions = [Make_active, Make_inactive]
    list_display = ('name_email', 'dept_id', 'hod', 'active')
    list_filter = ('dept_id', 'hod', 'active', 'timestamp')
    search_fields = ('name',)
    ordering = ('name',)
    fields = (
        ('name', 'auth_id'),
        ('dept_id', 'hod'),
        ('active',)
    )


@admin.register(Students)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('enrollment_no', 'Name', 'dept_id', 'div', 'semester')
    list_filter = ('dept_id', 'div', 'semester', 'timestamp')
    search_fields = ('first_name', 'last_name', 'enrollment_no')
    ordering = ('enrollment_no',)
    fields = (
        ('first_name', 'last_name'),
        ('auth_id', 'enrollment_no'),
        ('dept_id', 'semester', 'div')
    )


@admin.register(Subjects)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('Name_Code', 'subject_code', 'dept_id', 'div', 'semester', 'is_active')
    list_filter = ('dept_id', 'div', 'semester', 'is_active')
    search_fields = ('subject_name', 'subject_code')
    ordering = ('subject_name',)
    fields = (
        ('subject_name', 'subject_code'),
        ('dept_id', 'div', 'semester'),
        ('is_active',)
    )


@admin.register(Subject_to_Faculty_Mapping)
class Subject_Faculty_Mapping(admin.ModelAdmin):
    list_display = ('Faculty_Name', 'Subject_Name', 'Subject_Dept', 'Subject_Div', 'Subject_Semester')
    list_filter = ('subject_id__dept_id', 'subject_id__div', 'subject_id__semester')
    search_fields = ('faculty_id__name', 'subject_id__subject_name', 'subject_id__subject_code')
    ordering = ('faculty_id__name',)


admin.site.register(End_Sem_Feedback_Questions)


@admin.register(End_Sem_Feedback_Answers)
class EndSemFeedbackAdmin(admin.ModelAdmin):
    list_display = ('Feedback', 'Department', 'Division', 'Subject', 'Faculty', 'semester', 'timestamp')
    list_filter = ('subject_id__dept_id', 'subject_id__div', 'semester', 'timestamp')
    search_fields = (
        'subject_id__subject_name',
        'subject_id__subject_code',
        'faculty_id__name',
    )
    ordering = ('-timestamp',)
    # exclude = ('student_id',)
    readonly_fields = (
        'dept_id', 'subject_id', 'faculty_id', 'semester', 'student_id',
        'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'remarks', 'is_anonymous'
    )
    # fields = (
    #     ('dept_id', 'semester'),
    #     ('subject_id', 'faculty_id'),
    #     ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
    #     ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
    #     ('remarks', 'is_anonymous')
    # )

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id)
        if obj.is_anonymous:
            self.fields = (
                ('student_id', 'dept_id', 'semester'),
                ('subject_id', 'faculty_id'),
                ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
                ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
                ('remarks', 'is_anonymous')
            )
        else:
            self.fields = (
                ('dept_id', 'semester'),
                ('subject_id', 'faculty_id'),
                ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
                ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
                ('remarks', 'is_anonymous')
            )
        return obj

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Mid_Sem_Feedback_Questions)


@admin.register(Mid_Sem_Feedback_Answers)
class MidSemFeedbackAdmin(admin.ModelAdmin):
    list_display = ('Feedback', 'Department', 'Division', 'Subject', 'Faculty', 'semester', 'timestamp')
    list_filter = ('subject_id__dept_id', 'subject_id__div', 'semester', 'timestamp')
    search_fields = (
        'subject_id__subject_name',
        'subject_id__subject_code',
        'faculty_id__name',
    )
    ordering = ('-timestamp',)
    # exclude = ('student_id',)
    readonly_fields = (
        'dept_id', 'subject_id', 'faculty_id', 'semester', 'student_id',
        'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q10', 'remarks', 'is_anonymous'
    )

    # fields = (
    #     ('student_id', 'dept_id', 'semester'),
    #     ('subject_id', 'faculty_id'),
    #     ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
    #     ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
    #     ('remarks', 'is_anonymous')
    # )

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id)
        if obj.is_anonymous:
            self.fields = (
                ('student_id', 'dept_id', 'semester'),
                ('subject_id', 'faculty_id'),
                ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
                ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
                ('remarks', 'is_anonymous')
            )
        else:
            self.fields = (
                ('dept_id', 'semester'),
                ('subject_id', 'faculty_id'),
                ('Q1', 'Q2', 'Q3', 'Q4', 'Q5'),
                ('Q6', 'Q7', 'Q8', 'Q9', 'Q10'),
                ('remarks', 'is_anonymous')
            )
        return obj

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Committees)
class CommitteeAdmin(admin.ModelAdmin):
    list_display = ('committee_name', 'chairperson', 'timestamp')
    ordering = ('committee_name',)
    fields = (
        ('committee_name', 'chairperson'),
        'committee_details'
    )


@admin.register(Committee_to_Members_Mapping)
class Committee_to_memberAdmin(admin.ModelAdmin):
    list_display = ('committee_id', 'faculty_id', 'timestamp')
    list_filter = ('committee_id__committee_name', 'faculty_id__dept_id__dept_name')
    search_fields = ('committee_id__committee_name', 'faculty_id__name')
    ordering = ('committee_id',)
    fields = (
        ('committee_id', 'faculty_id'),
    )


@admin.register(Complaints)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('Student', 'Committee', 'status', 'reopened_count', 'timestamp')
    list_filter = ('committee_id__committee_name', 'status', 'reopened_count', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(Complaints_Solutions)
class Complaint_SolutionsAdmin(admin.ModelAdmin):
    list_display = ('Complaint', 'Committee', 'reopen_count', 'Faculty', 'timestamp')
    list_filter = ('complaint_id__committee_id__committee_name', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(Complaint_Reopen_comments)
class Complaint_Reopen_Admin(admin.ModelAdmin):
    list_display = ('Complaint', 'Committee', 'reopen_count', 'timestamp')
    list_filter = ('complaint_id__committee_id__committee_name', 'reopen_count', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('news_subject', 'Faculty', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('target_audience',)
    ordering = ('-timestamp',)


@admin.register(Student_Feedback_Status)
class FeedbackStatusAdmin(admin.ModelAdmin):
    list_display = ('Student', 'Subject', 'Faculty', 'Mid_Sem_Feedback', 'End_Sem_Feedback', 'timestamp')
    list_filter = ('student_id__dept_id__dept_name', 'student_id__div', 'student_id__semester', 'timestamp')
    ordering = ('-timestamp',)

    readonly_fields = ('student_id', 'subject_id', 'faculty_id', 'Mid_Sem_Feedback', 'End_Sem_Feedback')
    fields = (
        ('student_id', 'subject_id'),
        'faculty_id',
        ('Mid_Sem_Feedback', 'End_Sem_Feedback')
    )


@admin.register(Issues)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'timestamp')
    list_filter = ('timestamp',)
    ordering = ('-timestamp',)
