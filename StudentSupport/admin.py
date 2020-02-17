from django.contrib import admin
from .models import *
# Register your models here.

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