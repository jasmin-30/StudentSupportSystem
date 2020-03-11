import re

from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as st

from StudentSupport.models import *


# Create your views here.

def HomePageView(request):
    dept_qs = Departments.objects.all()
    # print(dept_qs)
    context = {
        "dept": dept_qs
    }
    if request.POST:
        if request.POST.get('email') is not None:
            email = request.POST.get('email')
            pwd = request.POST.get('pwd')
            role = request.POST.get('role')
            user = authenticate(request, username=email, password=pwd)
            if user is not None:
                if user.role == role:
                    # print(user)
                    login(request, user)
                    return HttpResponse("Logged in bro..")
                else:
                    # return HttpResponse("You are  not registered as" + role)
                    context["error"] = "You are  not registered as " + role
                    # print(context)
                    return render(request, 'index.html', context)
            else:
                # return HttpResponse("There was a problem logging in. Check your email or password again.")
                context["error"] = "There was a problem logging in. Check your email or password again."
                # print(context)
                return render(request, 'index.html', context)
    return render(request, 'index.html', context)


def StudentDashboard(request):
    return render(request, 'dashboard_student.html', context={})


def RegisterView(request):
    context = {}
    if request.method == "POST":
        fname = request.POST.get('fname')
        lname = request.POST.get('lname')
        email = request.POST.get('emailid')
        password = request.POST.get('password')
        enrollment_no = request.POST.get('enrollment')
        dept = request.POST.get('dept')
        sem = request.POST.get('sem')
        try:
            user = User.objects.create_user(email, password=password)
            print(user)
            email_to = email
            email_from = st.EMAIL_HOST_USER
            print(email_to, email_from)
            subject = "Confirm Your Email - Student Support System - GEC, Bhavnagar"
            html_message = render_to_string('confirm_email_template.html', {'first_name': fname})
            plain_message = strip_tags(html_message)
            recipient_list = [str(email_to)]
            # print(plain_message)
            status = send_mail(
                subject=subject,
                message=plain_message,
                from_email=email_from,
                recipient_list=recipient_list,
                html_message=html_message
            )
            print(status)
            if status == 1:
                student_obj = Students.objects.create(enrollment_no=enrollment_no,
                                                      first_name=fname,
                                                      last_name=lname,
                                                      auth_id=User.objects.get(id=user.id),
                                                      dept_id=Departments.objects.get(id=int(dept)),
                                                      semester=int(sem))
                student_obj.save()
                print(student_obj)
                context["success"] = "Registered Successfully"
                context["msg"] = "Please check your inbox for a confirmation email. Click the link in the email to confirm your email address."
                return render(request, "index.html", context)
            else:
                return HttpResponse("Error in sending email. Please try again after sometime.")
        except Exception as e:
            context["error"] = "Error in registering please try again later."
            return HttpResponse("Error" + str(e))

        # return HttpResponse("User Successfully Created")

    return HttpResponse("Register")
