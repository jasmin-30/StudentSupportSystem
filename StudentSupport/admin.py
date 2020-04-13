from django.contrib import admin
from django.contrib.auth import get_user_model
from .forms import UserAdminChangeForm, UserAdminCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import *

# Register your models here.
User = get_user_model()


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'admin', 'active')
    list_filter = ('admin', 'active', 'staff', 'role')
    fieldsets = (
        (None, {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('admin', 'active', 'staff')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)
admin.site.register(Departments)
admin.site.register(Principal)
admin.site.register(Faculty)
admin.site.register(Students)
admin.site.register(Subjects)
admin.site.register(Subject_to_Faculty_Mapping)
admin.site.register(End_Sem_Feedback_Questions)
admin.site.register(End_Sem_Feedback_Answers)
admin.site.register(Mid_Sem_Feedback_Questions)
admin.site.register(Mid_Sem_Feedback_Answers)
admin.site.register(Course_Exit_Survey_Questions)
admin.site.register(Course_Exit_Survey_Answers)
admin.site.register(Program_Exit_Survey_Questions)
admin.site.register(Program_Exit_Survey_Answers)
admin.site.register(Committee_Details)
admin.site.register(Committee_to_Members_Mapping)
admin.site.register(Complaints_of_Students)
admin.site.register(Complaints_of_Facultys)
admin.site.register(News)
admin.site.register(Student_Feedback_Status)
