import json
from base64 import b64encode, b64decode
from io import BytesIO
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as st
from django.db import *

from StudentSupport.models import *


# Create your views here.
def EditableTableView(request):
    fac_qs = Students.objects.all()
    dept_qs = Departments.objects.all()
    context = {
        "fac": fac_qs,
        "dept": dept_qs
    }
    return render(request, "Extra/editable-table.html", context)


def HomePageView(request):
    dept_qs = Departments.objects.all()
    # print(dept_qs)
    context = {
        "dept": dept_qs,
        "base_url": st.BASE_URL,
    }
    if request.POST:
        if request.POST.get('email_forgot') is not None:
            email_forgot = request.POST.get('email_forgot')
            try:
                user_obj = User.objects.get(email=email_forgot)
                student_obj = Students.objects.get(auth_id=user_obj)
            except Exception as e:
                print(e)
                context["error"] = "You are not a registered User."
                return render(request, "index.html", context)

            email_to = email_forgot
            email_from = st.EMAIL_HOST_USER
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "changePassword/?email=" + email_encrypted.decode('utf-8')
            # print(email_to, email_from)
            subject = "Recover Your Password."
            html_message = render_to_string('recover_password_template.html',
                                            {'first_name': student_obj.first_name, 'url': url})
            plain_message = strip_tags(html_message)
            recipient_list = [str(email_to)]
            # print(plain_message)
            status = send_mail(
                subject=subject,
                message=plain_message,
                from_email=email_from,
                recipient_list=recipient_list,
                html_message=html_message,
                fail_silently=True
            )
            print(status)
            if status == 1:
                context["success"] = "Email Sent Successfully"
                context["msg"] = "Check your inbox for further instructions to change your password."
                return render(request, "index.html", context)
            else:
                context["error"] = "Error in sending email. Check whether computer is connected to internet."
                return render(request, "index.html", context)

        if request.POST.get('email') is not None:
            email = request.POST.get('email')
            pwd = request.POST.get('pwd')
            role = request.POST.get('role')
            try:
                user_obj = User.objects.get(email=email)
            except User.DoesNotExist:
                context["error"] = "Email ID does not exist. Register first if you are student."
                return render(request, "index.html", context)

            if user_obj.is_active:
                user = authenticate(request, username=email, password=pwd)
                if user is not None:
                    if user.role == role:
                        # print(user)
                        login(request, user)  # Redirect to dashboard after login
                        request.session["User"] = str(user.id)
                        return HttpResponseRedirect("/" + role.lower() + "/dashboard/")
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
            else:
                context["error"] = "Please Activate your account. Check your inbox for Confirmation Email."
                return render(request, "index.html", context)

    return render(request, 'index.html', context)


def LogoutView(request):
    # return render(request, "logout.html", {})
    if request.user.is_authenticated:
        logout(request)
        request.session.clear()
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def StudentDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        user_obj = User.objects.get(id=request.session["User"])
        print(user_obj)
        std_obj = Students.objects.get(auth_id=user_obj)
        print(std_obj)
        try:
            news_qs = News.objects.order_by('-timestamp')[10]
        except IndexError as e:
            print(e)
            news_qs = News.objects.order_by('-timestamp')
            print(news_qs)

        print(news_qs)
        context["news"] = news_qs
        context["name"] = str(std_obj.first_name) + " " + str(std_obj.last_name)
        return render(request, 'dashboard_student.html', context)
    else:
        context["error"] = "Login First."
        return render(request, "index.html", context)


def FacultyDashboard(request):
    return render(request, 'dashboard_faculty.html', context={})


def CommitteeDashboard(request):
    return render(request, 'committee_dashboard.html', context={})


def FacultyViewDetailedFeedback(request):
    return render(request, 'view_detailed_feedback.html', context={})


def FacultyViewAverageFeedback(request):
    return render(request, 'view_average_feedback.html', context={})


def HodDashboard(request):
    return render(request, 'hod_dashboard.html', context={})


def HodViewDetailedFeedback(request):
    return render(request, 'hod_view_detailed_feedback.html', context={})


def HodViewAverageFeedback(request):
    return render(request, 'hod_view_average_feedback.html', context={})


def PrincipalDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        user_obj = User.objects.get(id=request.session["User"])
        principal_obj = Principal.objects.get(auth_id=user_obj)
        context["name"] = principal_obj.name
        return render(request, 'principal/principal_dashboard.html', context)
    else:
        return render(request, 'principal/principal_dashboard.html', context)


def ManageCommitteesView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        user_obj = User.objects.get(id=request.session["User"])
        principal_obj = Principal.objects.get(auth_id=user_obj)
        context["name"] = principal_obj.name
        committee_qs = Committee_Details.objects.all()
        context["committees"] = committee_qs
        faculty_qs = Faculty.objects.all()
        context["faculties"] = faculty_qs

        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                details = request.POST.get('details')
                chairperson = request.POST.get('chairperson')
                try:
                    obj = Committee_Details.objects.create(
                        committee_name=name,
                        committee_details=details,
                        chairperson=Faculty.objects.get(id=chairperson)
                    )
                    obj.save()
                    #Send Email to Chiarperson regarding committee details and motive
                    context["success"] = "Committee Created Successfully."
                    return render(request, "principal/manage_committees.html", context)

                except Faculty.DoesNotExist:
                    context["error"] = "Select Valid Chair person."
                    return render(request, "principal/manage_committees.html", context)

                except Exception as e:
                    print(e)
                    context["error"] = "Error in creating committee. Please Contact Developers."
                    return render(request, "principal/manage_committees.html", context)

        return render(request, 'principal/manage_committees.html', context)
    else:
        return render(request, 'index.html', context)


def EditCommittees(request):
    if request.user.is_authenticated:
        if request.user.role == "Principal":
            if request.method == "GET":
                if request.GET.get('info') is not None:
                    info = request.GET.get('info')
                    data = eval(info)
                    print(data)
                    if data['action'] == 'update':
                        try:
                            committee_obj = Committee_Details.objects.get(id=data['row_id'])
                            print(committee_obj)
                            committee_obj.committee_name = data['name']
                            committee_obj.committee_details = data['details']
                            committee_obj.chairperson = Faculty.objects.get(id=data['fac_id'])
                            committee_obj.save()
                            return HttpResponse("Data Updated Successfully.")

                        except Exception as e:
                            print(e)
                            return HttpResponse(e)

                    if data['action'] == 'delete':
                        try:
                            committee_obj = Committee_Details.objects.get(id=data['row_id']).delete()
                            return HttpResponse("Data Deleted Successfully.")

                        except Exception as e:
                            print(e)
                            return HttpResponse(e)
                else:
                    return HttpResponse("Error in parsing json data.")

        else:
            return HttpResponse("You are not authorized to perform this action.")
    else:
        return HttpResponse("Login First")


def StudentMidSemFeedbackView(request):
    return render(request, "student_mid_sem_feedback.html", context={})


def ConfirmAccountView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.method == "GET":
        if request.GET.get('email') is not None:
            raw_email = str(request.GET.get('email'))
            email = b64decode(raw_email.encode()).decode('utf-8')
            user_obj = User.objects.get(email=email)
            print(user_obj)
            user_obj.active = True
            user_obj.save()
            context["success"] = "Account Activated Successfully."
            context["msg"] = "Your Account has been Successfully activated. You can now access your profile."
            return render(request, "index.html", context)
    return HttpResponseRedirect("/")


def ManageDepartmentView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        dept_qs = Departments.objects.all()
        fac_qs = Faculty.objects.all()
        dept = []
        for i in dept_qs:
            tmp = {}
            tmp["id"] = i.id
            tmp["dept_name"] = i.dept_name
            tmp["hod"] = fac_qs.filter(dept_id=i.id)
            dept.append(tmp)
        context["dept"] = dept
        context["faculties"] = fac_qs
        return render(request, 'principal/manage_departments.html', context)


def StudentProfile(request):
    return render(request, 'student_profile_page.html', context={})


def FacultyProfile(request):
    return render(request, 'faculty_profile_page.html', context={})


def RegisterView(request):
    context = {
        "base_url": st.BASE_URL,
    }
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
        except IntegrityError as e:
            print(e)
            context["error"] = "Email ID is already Registered. Log in with valid credentials."
            return render(request, "index.html", context)

        email_to = str(email)
        email_from = str(st.EMAIL_HOST_USER)
        email_encrypted = b64encode(email_to.encode())
        url = st.BASE_URL + "activate/?email=" + email_encrypted.decode('utf-8')
        print(url)
        # print(email_to, email_from)
        subject = "Confirm Your Email - Student Support System - GEC, Bhavnagar"
        html_message = render_to_string('confirm_email_template.html', {'first_name': fname, 'url': url})
        plain_message = strip_tags(html_message)
        recipient_list = [str(email_to)]
        # print(plain_message)
        status = send_mail(
            subject=subject,
            message=plain_message,
            from_email=email_from,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True
        )
        print(status)
        if status == 1:
            try:
                student_obj = Students.objects.create(enrollment_no=enrollment_no,
                                                      first_name=fname,
                                                      last_name=lname,
                                                      auth_id=User.objects.get(id=user.id),
                                                      dept_id=Departments.objects.get(id=int(dept)),
                                                      semester=int(sem))
                student_obj.save()
                print(student_obj)
            except IntegrityError as e:
                print(e)
                context["error"] = "Enrollment Number Already Exists..."
                return render(request, "index.html", context)

            context["success"] = "Registered Successfully"
            context["msg"] = "Please check your inbox for a confirmation email. Click the link in the email to " \
                             "confirm your email address. "
            return render(request, "index.html", context)
        else:
            user.delete()
            context[
                "error"] = "Error in sending email please try again later. Check whether computer is connected to internet or not."
            return render(request, "index.html", context)
    else:
        return render(request, "index.html", context)


def ChangePasswordView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.method == "GET":
        if request.GET.get('email') is not None:
            raw_email = str(request.GET.get('email'))
            email = b64decode(raw_email.encode()).decode('utf-8')
            request.session["email"] = email
            return render(request, "change_password.html", {})

    if request.method == "POST":
        if "email" in request.session and request.POST.get('password') is not None:
            email = request.session["email"]
            password = request.POST.get('password')
            try:
                user_obj = User.objects.get(email=email)
                user_obj.set_password(password)
                user_obj.save()
            except User.DoesNotExist:
                context["error"] = "Email Address Does not exist."
                request.session.delete("email")
                return render(request, "index.html", context)

            except Exception as e:
                print(e)
                context[
                    "error"] = "Error in changing password. Try again later or if problem persists contact developer team."
                return render(request, "index.html", context)

            context["success"] = "Password Changed Successfully."
            context["msg"] = "You can now login with new password."
            request.session.delete("email")
            return render(request, "index.html", context)

    return HttpResponseRedirect("/")
