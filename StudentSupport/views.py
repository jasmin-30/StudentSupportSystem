import json
from base64 import b64encode, b64decode
from email.utils import decode_params
from io import BytesIO

from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as st
from django.db import *
from rest_framework import status

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
        # For Forgot Password.. > Start
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
        # Forgot Password > End

        # Login > Start
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


def RegisterView(request):
    context = {
        "base_url": st.BASE_URL,
    }

    if request.method == "POST":
        # Student Registration > Start
        if request.POST.get('fname') is not None:
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
            subject = "Confirm Your Account - Student Support System - GEC, Bhavnagar"
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
        # Student Registration > End

        # Faculty Registration > Start
        if request.POST.get('faculty-name') is not None:
            faculty_name = request.POST.get('faculty-name')
            faculty_email = request.POST.get('faculty-emailid')
            faculty_password = request.POST.get('faculty-password')
            faculty_dept = request.POST.get('faculty-dept')
            try:
                faculty_user = User.objects.create_user(
                    str(faculty_email),
                    password=str(faculty_password),
                    role="Faculty"
                )
                print(faculty_user)
            except IntegrityError as e:
                print(e)
                context["error"] = "Email ID is already Registered. Log in with valid credentials."
                return render(request, "index.html", context)

            email_to = faculty_email
            email_from = str(st.EMAIL_HOST_USER)
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "activate/?email=" + email_encrypted.decode('utf-8')
            print(url)
            # print(email_to, email_from)
            subject = "Confirm Your Account - Student Support System - GEC, Bhavnagar"
            html_message = render_to_string('confirm_email_template.html', {'first_name': faculty_name, 'url': url})
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
                    faculty_obj = Faculty.objects.create(name=faculty_name,
                                                         auth_id=User.objects.get(id=faculty_user.id),
                                                         dept_id=Departments.objects.get(id=int(faculty_dept)),
                                                         )
                    faculty_obj.save()
                    print(faculty_obj)
                except Exception as e:
                    print(e)
                    context["error"] = "Error Occured Please Try again later."
                    return render(request, "index.html", context)

                context["success"] = "Registered Successfully"
                context["msg"] = "Please check your inbox for a confirmation email. Click the link in the email to " \
                                 "confirm your email address. "
                return render(request, "index.html", context)
            else:
                faculty_user.delete()
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
        principal_obj = Principal.objects.get(auth_id=request.session["User"])
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
                    # Send Email to Chiarperson regarding committee details and motive
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
        if request.user.getRole == "Principal":
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
                            return HttpResponse("Data Updated Successfully.", status=status.HTTP_200_OK)

                        except Exception as e:
                            print(e)
                            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)

                    if data['action'] == 'delete':
                        try:
                            committee_obj = Committee_Details.objects.get(id=data['row_id']).delete()
                            return HttpResponse("Data Deleted Successfully.", status=status.HTTP_200_OK)

                        except Exception as e:
                            print(e)
                            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return HttpResponse("Error in parsing json data.", status=status.HTTP_400_BAD_REQUEST)

        else:
            return HttpResponse("You are not authorized to perform this action.", status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Login First", status=status.HTTP_400_BAD_REQUEST)

def ManageDepartmentView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_obj = Principal.objects.get(auth_id=request.session["User"])
        context["name"] = principal_obj.name
        dept_qs = Departments.objects.all()
        fac_qs = Faculty.objects.all()
        dept = []
        for i in dept_qs:
            tmp = {}
            tmp["id"] = i.id
            tmp["dept_name"] = i.dept_name
            try:
                tmp["hod"] = fac_qs.filter(dept_id=i.id, hod=True).values()[0]
            except:
                tmp["hod"] = fac_qs.filter(dept_id=i.id, hod=True)
            dept.append(tmp)
        context["dept"] = dept
        context["faculties"] = fac_qs
        return render(request, 'principal/manage_departments.html', context)


def FetchFaculties(request):
    if request.user.is_authenticated and request.user.getRole == "Principal":
        if request.method == "GET":
            if request.GET.get('info') is not None:
                data = request.GET.get('info')
                data = eval(data)
                print(data)
                try:
                    fac_qs = Faculty.objects.filter(dept_id=int(data["department_id"]))
                    if fac_qs.count() == 0:
                        return HttpResponse("Error in loading Faculty List please try again later.",
                                            status=status.HTTP_400_BAD_REQUEST)
                    data = {}
                    faculties = []
                    for i in fac_qs:
                        tmp = {}
                        tmp["id"] = i.id
                        tmp["name"] = i.name
                        tmp["dept_id"] = i.dept_id.id
                        tmp["auth_id"] = i.auth_id.id
                        faculties.append(tmp)

                    data["Faculties"] = faculties
                    return HttpResponse(json.dumps(faculties), content_type='application/json',
                                        status=status.HTTP_200_OK)
                except:
                    return HttpResponse("Error in loading Faculty List please try again later.",
                                        status=status.HTTP_400_BAD_REQUEST)

    return HttpResponse("Error in loading Faculty List please try again later.", status=status.HTTP_400_BAD_REQUEST)


def EditHOD(request):
    if request.user.is_authenticated:
        if request.user.getRole == "Principal":
            if request.method == "GET":
                if request.GET.get('info') is not None:
                    data = request.GET.get('info')
                    data = eval(data)
                    print(data)
                    try:
                        if (data["old_hod"] != '-1'):
                            old_hod = Faculty.objects.get(id=int(data["old_hod"]))
                            old_hod.hod = False
                            old_hod.save()
                            print("Old HOD: ", old_hod)
                            new_hod = Faculty.objects.get(id=int(data["fac_id"]))
                            print("New HOD: ", new_hod)
                            new_hod.hod = True
                            new_hod.save()
                            return HttpResponse(
                                "Head Of Department changed for " + str(new_hod.dept_id.dept_name) + " Department.",
                                status=status.HTTP_200_OK)
                        else:
                            new_hod = Faculty.objects.get(id=int(data["fac_id"]))
                            print("New HOD: ", new_hod)
                            new_hod.hod = True
                            new_hod.save()
                            return HttpResponse(
                                "Head Of Department Assigned for " + str(new_hod.dept_id.dept_name) + " Department.",
                                status=status.HTTP_200_OK)
                    except:
                        return HttpResponse("Error in changing Head ot the department. Please try again later.",
                                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return HttpResponse("You are not authorized to change Head of the department.",
                                status=status.HTTP_401_UNAUTHORIZED)
    else:
        return HttpResponse("Login First", status=status.HTTP_400_BAD_REQUEST)


def PrincipalProfile(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_obj = Principal.objects.get(auth_id=request.user)
        context["name"] = principal_obj.name
        context["email"] = request.user.email
        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                email = request.POST.get('email')
                if name != principal_obj.name or email != request.user.email:
                    principal_obj.name = name
                    principal_obj.save()
                    user_obj = User.objects.get(id=request.user.id)
                    user_obj.email = email
                    user_obj.save()
                    request.user = user_obj
                    context["success"] = "Profile Updated Successfully"
                    context["name"] = principal_obj.name
                    context["email"] = request.user.email
                    return render(request, 'principal/principal_profile_page.html', context)

                else:
                    return render(request, 'principal/principal_profile_page.html', context)
            elif request.POST.get('newpwd') is not None:
                print("Hello")
                oldpwd = request.POST.get('oldpwd')
                newpwd = request.POST.get('newpwd')
                pwd = request.user.password
                print(pwd)
                if check_password(oldpwd, pwd):
                    try:
                        user_obj = User.objects.get(id=request.user.id)
                        user_obj.set_password(str(newpwd))
                        user_obj.save()
                        update_session_auth_hash(request, user_obj)
                        context["success"] = "Password Changed Successfully."
                        return render(request, 'principal/principal_profile_page.html', context)
                    except Exception as e:
                        print(e)
                        context["error"] = "Error in changing password. please try again later."
                        return render(request, 'principal/principal_profile_page.html', context)
                else:
                    context["error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'principal/principal_profile_page.html', context)
        else:
            return render(request, 'principal/principal_profile_page.html', context)

    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'index.html', context)

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


def StudentProfile(request):
    return render(request, 'student_profile_page.html', context={})


def FacultyProfile(request):
    return render(request, 'faculty_profile_page.html', context={})
