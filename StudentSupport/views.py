import datetime
import json
import os
from base64 import b64encode, b64decode

from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import LabelOffset
from reportlab.graphics.shapes import Drawing, Image, String, Line
from reportlab.lib import colors
from reportlab.lib.formatters import DecimalFormatter
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, TableStyle, Spacer, Table, PageBreak

from .utils import *
import traceback

from django.contrib.auth.hashers import check_password
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings as st
from django.db import *
from rest_framework import status

from StudentSupport.models import *


# Authentication and Home Page Views > Start
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
                if user_obj.role == "Student":
                    obj = Students.objects.get(auth_id=user_obj)
                    name = str(obj.first_name) + " " + str(obj.last_name)

                elif user_obj.role == "Faculty":
                    obj = Faculty.objects.get(auth_id=user_obj)
                    name = str(obj.name)

                else:
                    obj = Principal.objects.get(auth_id=user_obj)
                    name = str(obj.name)

            except Exception as e:
                print(e)
                context["error"] = "You are not a registered User."
                return render(request, "home_auth/index.html", context)

            email_to = email_forgot
            email_from = st.EMAIL_HOST_USER
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "changePassword/?email=" + email_encrypted.decode('utf-8')
            # print(email_to, email_from)
            print(url)
            subject = "Recover Your Password."
            html_message = render_to_string('email_templates/recover_password_template.html',
                                            {'first_name': name, 'url': url})
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
                user_obj.requested_change_password = True
                user_obj.save()
                context["success"] = "Email Sent Successfully"
                context["msg"] = "Check your inbox for further instructions to change your password."
                return render(request, "home_auth/index.html", context)
            else:
                context["error"] = "Error in sending email. Check whether computer is connected to internet."
                return render(request, "home_auth/index.html", context)
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
                return render(request, "home_auth/index.html", context)

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
                        return render(request, 'home_auth/index.html', context)
                else:
                    # return HttpResponse("There was a problem logging in. Check your email or password again.")
                    context["error"] = "There was a problem logging in. Check your email or password again."
                    # print(context)
                    return render(request, 'home_auth/index.html', context)
            else:
                context["error"] = "Please Activate your account. Check your inbox for Confirmation Email."
                return render(request, "home_auth/index.html", context)

    logout(request)
    request.session.clear()
    return render(request, 'home_auth/index.html', context)


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
                return render(request, "home_auth/index.html", context)

            email_to = str(email)
            email_from = str(st.EMAIL_HOST_USER)
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "activate/?email=" + email_encrypted.decode('utf-8')
            print(url)
            # print(email_to, email_from)
            subject = "Confirm Your Account - Student Support System - GEC, Bhavnagar"
            html_message = render_to_string('email_templates/confirm_email_template.html',
                                            {'first_name': fname, 'url': url})
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
                    return render(request, "home_auth/index.html", context)

                context["success"] = "Registered Successfully"
                context["msg"] = "Please check your inbox for a confirmation email. Click the link in the email to " \
                                 "confirm your email address. "
                return render(request, "home_auth/index.html", context)
            else:
                user.delete()
                context[
                    "error"] = "Error in sending email please try again later. Check whether computer is connected to internet or not."
                return render(request, "home_auth/index.html", context)
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
                return render(request, "home_auth/index.html", context)

            email_to = faculty_email
            email_from = str(st.EMAIL_HOST_USER)
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "activate/?email=" + email_encrypted.decode('utf-8')
            print(url)
            # print(email_to, email_from)
            subject = "Confirm Your Account - Student Support System - GEC, Bhavnagar"
            html_message = render_to_string('email_templates/confirm_email_template.html',
                                            {'first_name': faculty_name, 'url': url})
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
                    return render(request, "home_auth/index.html", context)

                context["success"] = "Registered Successfully"
                context["msg"] = "Please check your inbox for a confirmation email. Click the link in the email to " \
                                 "confirm your email address. "
                return render(request, "home_auth/index.html", context)
            else:
                faculty_user.delete()
                context[
                    "error"] = "Error in sending email please try again later. Check whether computer is connected to internet or not."
                return render(request, "home_auth/index.html", context)


    else:
        return render(request, "home_auth/index.html", context)


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
            return render(request, "home_auth/index.html", context)
    return HttpResponseRedirect("/")


def ChangePasswordView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.method == "GET":
        if request.GET.get('email') is not None:
            raw_email = str(request.GET.get('email'))
            email = b64decode(raw_email.encode()).decode('utf-8')
            user_obj = User.objects.get(email=email)
            if user_obj.requested_change_password:
                request.session["email"] = email
                print(email)
                return render(request, "home_auth/forgot_password.html", context)
            else:
                # Send mail to owner that someone tried to change password.
                context["error"] = "Request to change password can not be processed. Please try again."
                return render(request, "home_auth/index.html", context)

    if request.method == "POST":
        if "email" in request.session and request.POST.get('password') is not None:
            email = request.session["email"]
            password = request.POST.get('password')
            try:
                user_obj = User.objects.get(email=email)
                print(user_obj)
                user_obj.set_password(password)
                user_obj.requested_change_password = False
                user_obj.save()
            except User.DoesNotExist:
                context["error"] = "Email Address Does not exist."
                request.session.delete("email")
                return render(request, "home_auth/index.html", context)

            except Exception as e:
                print(e)
                context[
                    "error"] = "Error in changing password. Try again later or if problem persists contact developer team."
                return render(request, "home_auth/index.html", context)

            context["success"] = "Password Changed Successfully."
            context["msg"] = "You can now login with new password."
            request.session.delete("email")
            return render(request, "home_auth/index.html", context)

    return HttpResponseRedirect("/")


# Authentication and Home Page Views > End


# Student Related Views > Start
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
        return render(request, 'students/dashboard_student.html', context)
    else:
        context["error"] = "Login First."
        return render(request, "home_auth/index.html", context)


def StudentProfile(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        student_obj = Students.objects.get(auth_id=request.user)
        context["std_obj"] = student_obj
        context["name"] = str(student_obj.first_name) + " " + str(student_obj.last_name)
        context["email"] = request.user.email

        if request.method == "POST":
            if request.POST.get('fname') is not None:
                try:
                    user_obj = User.objects.get(id=request.user.id)
                    fname = request.POST.get('fname')
                    lname = request.POST.get('lname')
                    email = request.POST.get('email')

                    student_obj.first_name = fname
                    student_obj.last_name = lname
                    student_obj.save()

                    user_obj.email = email
                    user_obj.save()
                    request.user = user_obj

                    context["std_obj"] = student_obj
                    context["email"] = request.user.email

                    context["success"] = "Profile has been updated successfully."
                    return render(request, 'students/student_profile_page.html', context)

                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    context["error"] = "Some technical problem occured. Please try again later."
                    return render(request, 'students/student_profile_page.html', context)

            elif request.POST.get('sem') is not None:
                try:
                    sem = request.POST.get('sem')
                    student_obj.semester = sem
                    student_obj.save()

                    context["std_obj"] = student_obj
                    context["success"] = "Semester has been updated successfully."
                    return render(request, 'students/student_profile_page.html', context)

                except Exception as e:
                    traceback.print_exc()
                    print(e)
                    context["error"] = "Some technical problem occured. Please try again later."
                    return render(request, 'students/student_profile_page.html', context)

            elif request.POST.get('newpwd') is not None:
                oldpwd = request.POST.get('oldpwd')
                newpwd = request.POST.get('newpwd')
                pwd = request.user.password
                if check_password(oldpwd, pwd):
                    try:
                        user_obj = User.objects.get(id=request.user.id)
                        user_obj.set_password(str(newpwd))
                        user_obj.save()
                        update_session_auth_hash(request, user_obj)

                        context["success"] = "Password has been changed successfully!"
                        return render(request, 'students/student_profile_page.html', context)

                    except Exception as e:
                        print(e)
                        context["error"] = "Error in changing password. please try again later."
                        context["name"] = str(student_obj.first_name) + " " + str(student_obj.last_name)
                        context["email"] = request.user.email
                        return render(request, 'students/student_profile_page.html', context)

                else:
                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'students/student_profile_page.html', context)
        else:
            return render(request, 'students/student_profile_page.html', context)

    else:
        context["error"] = "Login to access your profile."
        return render(request, 'home_auth/index.html', context)


def StudentFeedbackSection(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        std_obj = Students.objects.get(auth_id=request.user)
        dept_id = std_obj.dept_id
        context["name"] = str(std_obj.first_name) + " " + str(std_obj.last_name)
        if type == 'mid-sem':
            questions = Mid_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            context["remark"] = (questions.count() + 1)

            current_sem = std_obj.semester
            subject = []
            for i in range(1, current_sem + 1):
                tmp_list = []
                subject_qs = Subjects.objects.filter(dept_id=dept_id, semester=i)
                if subject_qs.count() == 0:
                    tmp = {
                        'status': 0
                    }
                    tmp_list.append(tmp)
                    subject.append(tmp_list)

                else:
                    for j in subject_qs:
                        tmp = {
                            'id': j.id,
                            'name': j.subject_name,
                            'code': j.subject_code
                        }

                        teaching_faculty_qs = Subject_to_Faculty_Mapping.objects.filter(subject_id=j)
                        faculties = []
                        for k in teaching_faculty_qs:
                            tmp1 = {
                                'fac_id': k.faculty_id.id,
                                'fac_name': k.faculty_id.name
                            }
                            try:
                                feedback_status_obj = Student_Feedback_Status.objects.get(student_id=std_obj,
                                                                                          faculty_id=k.faculty_id,
                                                                                          subject_id=j)
                                if feedback_status_obj.mid_sem_feedback is not None:
                                    tmp1['mid_sem_obj'] = feedback_status_obj.id

                                else:
                                    tmp1['mid_sem_obj'] = None

                            except Student_Feedback_Status.DoesNotExist:
                                print("Mid semester object does not exist for:", j, k)
                                tmp1['mid_sem_obj'] = None
                            faculties.append(tmp1)

                        tmp['teaching_faculties'] = faculties
                        tmp['status'] = 1
                        tmp_list.append(tmp)

                    subject.append(tmp_list)

            context["semesters"] = subject

            if request.method == 'POST':
                if request.POST.get('subject_id') is not None:
                    try:
                        std_obj = Students.objects.get(auth_id=request.user)

                        dept_obj = Departments.objects.get(id=std_obj.dept_id.id)

                        sub_id = request.POST.get('subject_id')
                        sub_obj = Subjects.objects.get(id=int(sub_id))

                        fac_id = request.POST.get('faculty_id')
                        fac_obj = Faculty.objects.get(id=int(fac_id))

                        semester = sub_obj.semester

                        ans1 = request.POST.get('rating_1') if request.POST.get('rating_1') else 0
                        ans2 = request.POST.get('rating_2') if request.POST.get('rating_2') else 0
                        ans3 = request.POST.get('rating_3') if request.POST.get('rating_3') else 0
                        ans4 = request.POST.get('rating_4') if request.POST.get('rating_4') else 0
                        ans5 = request.POST.get('rating_5') if request.POST.get('rating_5') else 0
                        ans6 = request.POST.get('rating_6') if request.POST.get('rating_6') else 0
                        ans7 = request.POST.get('rating_7') if request.POST.get('rating_7') else 0
                        ans8 = request.POST.get('rating_8') if request.POST.get('rating_8') else 0
                        ans9 = request.POST.get('rating_9') if request.POST.get('rating_9') else 0
                        ans10 = request.POST.get('rating_10') if request.POST.get('rating_10') else 0
                        remarks = request.POST.get('remark') if request.POST.get('remark') else None
                        # print(ans1,ans2, ans3, ans4, ans5, ans6, ans7, ans8, ans9, ans10, remarks)

                        mid_sem_feedback_ans_obj, is_created = Mid_Sem_Feedback_Answers.objects.get_or_create(
                            student_id=std_obj,
                            dept_id=dept_obj,
                            subject_id=sub_obj,
                            faculty_id=fac_obj,
                            semester=semester,
                            defaults={
                                'Q1': int(ans1), 'Q2': int(ans2), 'Q3': int(ans3), 'Q4': int(ans4), 'Q5': int(ans5),
                                'Q6': int(ans6), 'Q7': int(ans7), 'Q8': int(ans8), 'Q9': int(ans9), 'Q10': int(ans10),
                                'remarks': remarks
                            }
                        )
                        mid_sem_feedback_ans_obj.save()
                        if is_created:
                            obj, created_obj = Student_Feedback_Status.objects.get_or_create(
                                student_id=std_obj,
                                subject_id=sub_obj,
                                faculty_id=fac_obj,
                                defaults={
                                    'mid_sem_feedback': mid_sem_feedback_ans_obj
                                }
                            )
                            if not created_obj:
                                obj.mid_sem_feedback = mid_sem_feedback_ans_obj

                            obj.save()

                            context["success"] = "Thank you for giving your feedback."
                            context["msg"] = "Mid Semester Feedback for " + str(
                                fac_obj.name) + " has been saved successfully."
                            return render(request, "students/student_mid_sem_feedback.html", context)

                        else:
                            context["error"] = "You have already given feedback for " + str(fac_obj.name)
                            return render(request, "students/student_mid_sem_feedback.html", context)

                    except Exception as e:
                        traceback.print_exc()
                        print(e)
                        context["error"] = "Some technical problem occured."
                        return render(request, "students/student_mid_sem_feedback.html", context)
                else:
                    context["error"] = "Some technical problem occured."
                    return render(request, "students/student_mid_sem_feedback.html", context)

            else:
                return render(request, "students/student_mid_sem_feedback.html", context)

        elif type == 'end-sem':
            questions = End_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            context["remark"] = (questions.count() + 1)

            current_sem = std_obj.semester
            subject = []
            for i in range(1, current_sem + 1):
                tmp_list = []
                subject_qs = Subjects.objects.filter(dept_id=dept_id, semester=i)
                if subject_qs.count() == 0:
                    tmp = {
                        'status': 0
                    }
                    tmp_list.append(tmp)
                    subject.append(tmp_list)

                else:
                    for j in subject_qs:
                        tmp = {
                            'id': j.id,
                            'name': j.subject_name,
                            'code': j.subject_code
                        }

                        teaching_faculty_qs = Subject_to_Faculty_Mapping.objects.filter(subject_id=j)
                        faculties = []
                        for k in teaching_faculty_qs:
                            tmp1 = {
                                'fac_id': k.faculty_id.id,
                                'fac_name': k.faculty_id.name
                            }
                            try:
                                feedback_status_obj = Student_Feedback_Status.objects.get(student_id=std_obj,
                                                                                          faculty_id=k.faculty_id,
                                                                                          subject_id=j)
                                if feedback_status_obj.end_sem_feedback is not None:
                                    tmp1['end_sem_obj'] = feedback_status_obj.id

                                else:
                                    tmp1['end_sem_obj'] = None

                            except Student_Feedback_Status.DoesNotExist:
                                print("End semester object does not exist for:", j, k)
                                tmp1['end_sem_obj'] = None
                            faculties.append(tmp1)

                        tmp['teaching_faculties'] = faculties
                        tmp['status'] = 1
                        tmp_list.append(tmp)

                    subject.append(tmp_list)

            context["semesters"] = subject

            if request.method == 'POST':
                if request.POST.get('subject_id') is not None:
                    try:
                        std_obj = Students.objects.get(auth_id=request.user)

                        dept_obj = Departments.objects.get(id=std_obj.dept_id.id)

                        sub_id = request.POST.get('subject_id')
                        sub_obj = Subjects.objects.get(id=int(sub_id))

                        fac_id = request.POST.get('faculty_id')
                        fac_obj = Faculty.objects.get(id=int(fac_id))

                        semester = sub_obj.semester

                        ans1 = request.POST.get('rating_1') if request.POST.get('rating_1') else 0
                        ans2 = request.POST.get('rating_2') if request.POST.get('rating_2') else 0
                        ans3 = request.POST.get('rating_3') if request.POST.get('rating_3') else 0
                        ans4 = request.POST.get('rating_4') if request.POST.get('rating_4') else 0
                        ans5 = request.POST.get('rating_5') if request.POST.get('rating_5') else 0
                        ans6 = request.POST.get('rating_6') if request.POST.get('rating_6') else 0
                        ans7 = request.POST.get('rating_7') if request.POST.get('rating_7') else 0
                        ans8 = request.POST.get('rating_8') if request.POST.get('rating_8') else 0
                        ans9 = request.POST.get('rating_9') if request.POST.get('rating_9') else 0
                        ans10 = request.POST.get('rating_10') if request.POST.get('rating_10') else 0
                        remarks = request.POST.get('remark') if request.POST.get('remark') else None

                        end_sem_feedback_ans_obj, is_created = End_Sem_Feedback_Answers.objects.get_or_create(
                            student_id=std_obj,
                            dept_id=dept_obj,
                            subject_id=sub_obj,
                            faculty_id=fac_obj,
                            semester=semester,
                            defaults={
                                'Q1': int(ans1), 'Q2': int(ans2), 'Q3': int(ans3), 'Q4': int(ans4), 'Q5': int(ans5),
                                'Q6': int(ans6), 'Q7': int(ans7), 'Q8': int(ans8), 'Q9': int(ans9), 'Q10': int(ans10),
                                'remarks': remarks
                            }
                        )
                        end_sem_feedback_ans_obj.save()
                        if is_created:
                            obj, created_obj = Student_Feedback_Status.objects.get_or_create(
                                student_id=std_obj,
                                subject_id=sub_obj,
                                faculty_id=fac_obj,
                                defaults={
                                    'end_sem_feedback': end_sem_feedback_ans_obj
                                }
                            )
                            if not created_obj:
                                obj.end_sem_feedback = end_sem_feedback_ans_obj

                            obj.save()

                            context["success"] = "Thank you for giving your feedback."
                            context["msg"] = "End Semester Feedback for " + str(
                                fac_obj.name) + " has been saved successfully."
                            return render(request, "students/student_end_sem_feedback.html", context)

                        else:
                            context["error"] = "You have already given feedback for " + str(fac_obj.name)
                            return render(request, "students/student_end_sem_feedback.html", context)

                    except Exception as e:
                        traceback.print_exc()
                        print(e)
                        context["error"] = "Some technical problem occured."
                        return render(request, "students/student_end_sem_feedback.html", context)

                else:
                    context["error"] = "Some technical problem occured."
                    return render(request, "students/student_end_sem_feedback.html", context)

            else:
                return render(request, "students/student_end_sem_feedback.html", context)

        else:
            return HttpResponse("<h1>404 Page Not Found</h1>")

    else:
        context["error"] = "Login First"
        return render(request, 'home_auth/index.html', context)


def GetFeedback(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            if request.GET.get('obj_id') is not None:
                type = request.GET.get('type')
                obj_id = request.GET.get('obj_id')
                if type == "mid":
                    feedback_obj = Mid_Sem_Feedback_Answers.objects.get(
                        id=Student_Feedback_Status.objects.get(id=int(obj_id)).mid_sem_feedback.id
                    )
                    data = {
                        'id': feedback_obj.id,
                        'subject_name': feedback_obj.subject_id.subject_name,
                        'faculty_name': feedback_obj.faculty_id.name,
                        'ans_1': feedback_obj.Q1, 'ans_2': feedback_obj.Q2,
                        'ans_3': feedback_obj.Q3, 'ans_4': feedback_obj.Q4,
                        'ans_5': feedback_obj.Q5, 'ans_6': feedback_obj.Q6,
                        'ans_7': feedback_obj.Q7, 'ans_8': feedback_obj.Q8,
                        'ans_9': feedback_obj.Q9, 'ans_10': feedback_obj.Q10,
                        'remarks': feedback_obj.remarks,
                        'date': str(feedback_obj.timestamp.strftime("%d %B, %Y %I:%M %p"))
                    }
                    res = json.dumps(data)
                    return HttpResponse(res, status=status.HTTP_200_OK)

                elif type == "end":
                    feedback_obj = End_Sem_Feedback_Answers.objects.get(
                        id=Student_Feedback_Status.objects.get(id=int(obj_id)).end_sem_feedback.id
                    )
                    data = {
                        'id': feedback_obj.id,
                        'subject_name': feedback_obj.subject_id.subject_name,
                        'faculty_name': feedback_obj.faculty_id.name,
                        'ans_1': feedback_obj.Q1, 'ans_2': feedback_obj.Q2,
                        'ans_3': feedback_obj.Q3, 'ans_4': feedback_obj.Q4,
                        'ans_5': feedback_obj.Q5, 'ans_6': feedback_obj.Q6,
                        'ans_7': feedback_obj.Q7, 'ans_8': feedback_obj.Q8,
                        'ans_9': feedback_obj.Q9, 'ans_10': feedback_obj.Q10,
                        'remarks': feedback_obj.remarks,
                        'date': str(feedback_obj.timestamp.strftime("%d %B, %Y %I:%M %p"))
                    }
                    res = json.dumps(data)
                    return HttpResponse(res, status=status.HTTP_200_OK)

                else:
                    data = {
                        "error": "Can not find what you are looking for."
                    }
                    res = json.dumps(data)
                    return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

            else:
                data = {
                    "error": "Feedback Object Not passed"
                }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

        else:
            data = {
                "error": "Error in parsing data."
            }
            res = json.dumps(data)
            return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    else:
        data = {
            "error": "Login First"
        }
        res = json.dumps(data)
        return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


def StudentComplaintSectionView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        std_obj = Students.objects.get(auth_id=request.user)
        context["name"] = str(std_obj.first_name) + " " + str(std_obj.last_name)
        committee_qs = Committees.objects.all()
        context["committees"] = committee_qs

        if request.method == 'POST':
            if request.POST.get('complaint') is not None:
                complaint = request.POST.get('complaint')
                committee_id = request.POST.get('committee')
                complaint_obj = Complaints.objects.create(
                    student_id=std_obj,
                    complaint_details=complaint,
                    committee_id=Committees.objects.get(id=int(committee_id)),
                    status="Pending"
                )
                complaint_obj.save()

                context["success"] = "Complaint Registered successfully."

            if request.POST.get('complaint_id') is not None:
                complaint_id = request.POST.get('complaint_id')
                complaint_obj = Complaints.objects.get(id=int(complaint_id))
                status = request.POST.get('status')

                if status == "Pending" or status == "Revoke":
                    revoke_reason = request.POST.get('revoke_reason')
                    complaint_obj.status = "Revoked"
                    complaint_obj.revoked_reason = revoke_reason
                    complaint_obj.revoked = True
                    complaint_obj.revoked_date = datetime.datetime.now()
                    complaint_obj.save()

                    context["success"] = "Complaint Revoked Successfully."

                elif status == "Re-Open":
                    comment = request.POST.get('comment')
                    complaint_obj.status = "Re-Opened"
                    complaint_obj.reopened_count += 1
                    complaint_obj.save()

                    new_comment_obj = Complaint_Reopen_comments.objects.create(
                        complaint_id=complaint_obj,
                        reopen_count=complaint_obj.reopened_count,
                        comments=comment
                    )
                    new_comment_obj.save()

                    context["success"] = "Complaint thread has been re-opened."

        complaints_qs = Complaints.objects.filter(student_id=std_obj)
        # ======================== Pending Complaints ===================================
        pending_qs = complaints_qs.filter(status="Pending").filter(revoked=False).order_by('-timestamp')
        pending_count = pending_qs.count()
        if pending_count == 0:
            context["no_pending_complaints"] = True

        else:
            context["no_pending_complaints"] = False

        context["pending_count"] = pending_count

        pending_dict = []

        for i in pending_qs:
            tmp = {
                'id': i.id,
                'complaint_details': i.complaint_details,
                'committee': Committees.objects.get(id=i.committee_id.id).committee_name,
                'status': i.status,
                'timestamp': i.timestamp.strftime("%d %B, %Y %I:%M %p"),
            }
            pending_dict.append(tmp)

        context["pending_complaints"] = pending_dict
        # ======================== Re-Opened Complaints =================================
        reopened_qs = complaints_qs.filter(status="Re-Opened").filter(revoked=False).order_by('-timestamp')
        reopened_count = reopened_qs.count()
        if reopened_count == 0:
            context["no_reopened_complaints"] = True

        else:
            context["no_reopened_complaints"] = False

        context["reopened_count"] = reopened_count

        reopened_dict = []

        for i in reopened_qs:
            tmp = {
                'id': i.id,
                'complaint_details': i.complaint_details,
                'committee': Committees.objects.get(id=i.committee_id.id).committee_name,
                'reopened_count': i.reopened_count,
                'status': i.status,
                'timestamp': i.timestamp.strftime("%d %B, %Y %I:%M %p"),
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': str(std_obj.first_name) + " " + str(std_obj.last_name),
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)
                    try:
                        faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': faculty_response.reacting_faculty.name,
                            'comment': faculty_response.action,
                            'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                            'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)

                    except Complaints_Solutions.DoesNotExist:
                        pass

                j += 1

            reopened_dict.append(tmp)

        context["reopened_complaints"] = reopened_dict
        # ======================== Closed Complaints ====================================
        closed_qs = complaints_qs.filter(status="Closed").filter(revoked=False).order_by('-timestamp')
        closed_count = closed_qs.count()
        if closed_count == 0:
            context["no_closed_complaints"] = True

        else:
            context["no_closed_complaints"] = False

        context["closed_count"] = closed_count

        closed_dict = []

        for i in closed_qs:
            tmp = {
                'id': i.id,
                'complaint_details': i.complaint_details,
                'committee': Committees.objects.get(id=i.committee_id.id).committee_name,
                'reopened_count': i.reopened_count,
                'status': i.status,
                'timestamp': i.timestamp.strftime("%d %B, %Y %I:%M %p"),
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': str(std_obj.first_name) + " " + str(std_obj.last_name),
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)

                    faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': faculty_response.reacting_faculty.name,
                        'comment': faculty_response.action,
                        'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                        'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)

                j += 1

            closed_dict.append(tmp)

        context["closed_complaints"] = closed_dict
        # ======================== Revoked Complaints ===================================
        revoked_qs = complaints_qs.filter(status="Revoked").filter(revoked=True).order_by('-timestamp')
        revoked_count = revoked_qs.count()
        if revoked_count == 0:
            context["no_revoked_complaints"] = True

        else:
            context["no_revoked_complaints"] = False

        context["revoked_count"] = revoked_count

        revoked_dict = []

        for i in revoked_qs:
            tmp = {
                'id': i.id,
                'complaint_details': i.complaint_details,
                'committee': Committees.objects.get(id=i.committee_id.id).committee_name,
                'reopened_count': i.reopened_count,
                'status': i.status,
                'revoked_reason': i.revoked_reason,
                'revoked_date': str(i.revoked_date.strftime("%d %B, %Y %I:%M %p")),
                'timestamp': i.timestamp.strftime("%d %B, %Y %I:%M %p"),
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            if actions_count > 0:
                j = 0
                while j <= actions_count:
                    # print("yes")
                    if j < 1:
                        response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': response_obj.reacting_faculty.name,
                            'comment': response_obj.action,
                            'dept': response_obj.reacting_faculty.dept_id.dept_name,
                            'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)
                    else:
                        student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': str(std_obj.first_name) + " " + str(std_obj.last_name),
                            'comment': student_response.comments,
                            'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Re-Opened'
                        }
                        tmp["actions"].append(tmp1)
                        try:
                            faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                            tmp1 = {
                                'name': faculty_response.reacting_faculty.name,
                                'comment': faculty_response.action,
                                'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                                'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                                'action': 'Closed'
                            }
                            tmp["actions"].append(tmp1)

                        except Complaints_Solutions.DoesNotExist:
                            pass

                    j += 1
            else:
                tmp["actions"] = []

            revoked_dict.append(tmp)

        context["revoked_complaints"] = revoked_dict

        return render(request, "students/student_complaint_section.html", context)

    else:
        context["error"] = "Login to access this page."
        return render(request, 'home_auth/index.html', context)


# Student Related Views > End


# Faculty Related Views > Start
# def FacultyDashboard(request):
#     context = {
#         "base_url": st.BASE_URL,
#     }
#     if request.user.is_authenticated:
#         fac_obj = Faculty.objects.get(auth_id=request.user)
#         if (fac_obj.hod):
#             return HttpResponseRedirect('/hod/dashboard')
#         context["name"] = fac_obj.name
#         try:
#             news_qs = News.objects.order_by('-timestamp')[10]
#         except IndexError as e:
#             print(e)
#             news_qs = News.objects.order_by('-timestamp')
#             print(news_qs)
#
#         print(news_qs)
#         context["news"] = news_qs
#         if not fac_obj.active:
#             context[
#                 "pnotify"] = "You have been removed from " + fac_obj.dept_id.dept_name + " Department. But you can still access feedback."
#
#         return render(request, 'faculty/dashboard_faculty.html', context)
#     else:
#         context["error"] = "Login to access dashboard."
#         return render(request, 'faculty/dashboard_faculty.html', context)

def FacultyDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        print(fac_obj)
        if fac_obj.hod:
            return HttpResponseRedirect('/hod/dashboard/')
        committeeqs = Committee_to_Members_Mapping.objects.filter(faculty_id=fac_obj)
        committee_list = []
        for i in committeeqs:
            tmp = {
                'id': i.committee_id.id,
                'name': i.committee_id.committee_name,
                'chairperson': i.committee_id.chairperson.name,
                'members': Committee_to_Members_Mapping.objects.filter(committee_id=i.committee_id.id).count()
            }
            committee_list.append(tmp)
        context["committees"] = committee_list
        departments = Departments.objects.all()

        try:
            news_qs = News.objects.order_by('-timestamp')[10]
        except IndexError as e:
            print(e)
            news_qs = News.objects.order_by('-timestamp')
            print(news_qs)

        print(news_qs)
        context["news"] = news_qs
        context["name"] = str(fac_obj.name)
        context["dept"] = fac_obj.dept_id
        context["departments"] = departments

        if request.method == 'POST':
            try:
                dept_list_for_publish_news = []
                if request.POST.get('dept_all') is not None:
                    for i in range(len(departments)):
                        dept_list_for_publish_news.append(i + 1)

                    news_subject = request.POST.get('newstitle')
                    news_details = request.POST.get('newsdesc')

                    news_obj = News.objects.create(news_subject=news_subject,
                                                   news_details=news_details,
                                                   issuing_faculty=fac_obj
                                                   )
                    news_obj.save()

                    for i in range(len(dept_list_for_publish_news)):
                        news_obj.target_audience.add(Departments.objects.get(id=dept_list_for_publish_news[i]))

                else:
                    for i in range(len(departments)):
                        if (request.POST.get('dept' + str(i + 1)) is not None):
                            dept_list_for_publish_news.append(i + 1)

                    news_subject = request.POST.get('newstitle')
                    news_details = request.POST.get('newsdesc')

                    news_obj = News.objects.create(news_subject=news_subject,
                                                   news_details=news_details,
                                                   issuing_faculty=fac_obj
                                                   )
                    news_obj.save()
                    for i in range(len(dept_list_for_publish_news)):
                        news_obj.target_audience.add(Departments.objects.get(id=dept_list_for_publish_news[i]))
                context["success"] = "News published successfully."
                return render(request, 'faculty/dashboard_faculty.html', context)
            except:
                context["error"] = "Some technical problem occured."
                return render(request, 'faculty/dashboard_faculty.html', context)
        else:
            return render(request, 'faculty/dashboard_faculty.html', context)
    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login First."
        }
        return render(request, "home_auth/index.html", context)


def FacultyViewDetailedFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Faculty":
        fac_object = Faculty.objects.get(auth_id=request.user)
        context['name'] = fac_object.name
        context['fac_id'] = fac_object.id
        context['dept_name'] = fac_object.dept_id.dept_name
        subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=fac_object)
        subject_list = {
            'odd': [],
            'even': []
        }
        for i in subject_qs:
            if int(i.subject_id.semester) % 2:
                tmp = {
                    'subject_id': i.subject_id.id,
                    'subject_name': i.subject_id.subject_name,
                    'subject_code': i.subject_id.subject_code,
                    'subject_semester': i.subject_id.semester
                }
                subject_list["odd"].append(tmp)

            else:
                tmp = {
                    'subject_id': i.subject_id.id,
                    'subject_name': i.subject_id.subject_name,
                    'subject_code': i.subject_id.subject_code,
                    'subject_semester': i.subject_id.semester
                }
                subject_list["even"].append(tmp)

        print(subject_list)
        context["subject_list"] = json.dumps(subject_list)

        if type == "mid-sem":
            questions = Mid_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            return render(request, 'faculty/Detailed_Feedback/detailed_feedback_mid_sem.html', context)

        elif type == "end-sem":
            questions = End_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            return render(request, 'faculty/Detailed_Feedback/detailed_feedback_end_sem.html', context)

        else:
            context["error"] = "Page not found."
            return render(request, 'faculty/dashboard_faculty.html', context)
    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


def FacultyViewAverageFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Faculty":
        fac_object = Faculty.objects.get(auth_id=request.user)
        context['name'] = fac_object.name
        context['fac_id'] = fac_object.id
        subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=fac_object)
        subject_list = {
            'odd': [],
            'even': []
        }
        for i in subject_qs:
            if int(i.subject_id.semester) % 2:
                tmp = {
                    'subject_id': i.subject_id.id,
                    'subject_name': i.subject_id.subject_name,
                    'subject_code': i.subject_id.subject_code,
                    'subject_semester': i.subject_id.semester
                }
                subject_list["odd"].append(tmp)

            else:
                tmp = {
                    'subject_id': i.subject_id.id,
                    'subject_name': i.subject_id.subject_name,
                    'subject_code': i.subject_id.subject_code,
                    'subject_semester': i.subject_id.semester
                }
                subject_list["even"].append(tmp)

        print(subject_list)
        context["subject_list"] = json.dumps(subject_list)

        if type == "mid-sem":
            questions = Mid_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            return render(request, 'faculty/Average_Feedback/average_feedback_mid_sem.html', context)

        elif type == "end-sem":
            questions = End_Sem_Feedback_Questions.objects.all()
            context["questions"] = questions
            return render(request, 'faculty/Average_Feedback/average_feedback_end_sem.html', context)

        else:
            context["error"] = "Page not found."
            return render(request, 'faculty/dashboard_faculty.html', context)

    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


# def FacultyProfile(request):
#     context = {
#         "base_url": st.BASE_URL,
#     }
#     if request.user.is_authenticated and request.user.getRole == "Faculty":
#         fac_obj = Faculty.objects.get(auth_id=request.user)
#         context["name"] = fac_obj.name
#         context["email"] = request.user.email
#         context["dept"] = fac_obj.dept_id.dept_name
#         dept_qs = Departments.objects.all()
#         context["departments"] = dept_qs
#         if request.method == "POST":
#             if request.POST.get('name') is not None:
#                 name = request.POST.get('name')
#                 email = request.POST.get('email')
#                 dept = request.POST.get('dept')
#                 if name != fac_obj.name or email != request.user.email or dept != fac_obj.dept_id.id:
#                     fac_obj.name = name
#                     fac_obj.dept_id = Departments.objects.get(id=int(dept))
#                     fac_obj.save()
#                     user_obj = User.objects.get(id=request.user.id)
#                     user_obj.email = email
#                     user_obj.save()
#                     request.user = user_obj
#                     context["success"] = "Profile Updated Successfully"
#                     context["name"] = fac_obj.name
#                     context["email"] = request.user.email
#                     context["dept"] = fac_obj.dept_id.dept_name
#                     return render(request, 'faculty/faculty_profile_page.html', context)
#
#                 else:
#                     return render(request, 'faculty/faculty_profile_page.html', context)
#
#             elif request.POST.get('newpwd') is not None:
#                 oldpwd = request.POST.get('oldpwd')
#                 newpwd = request.POST.get('newpwd')
#                 pwd = request.user.password
#                 print(pwd)
#                 if check_password(oldpwd, pwd):
#                     try:
#                         user_obj = User.objects.get(id=request.user.id)
#                         user_obj.set_password(str(newpwd))
#                         user_obj.save()
#                         update_session_auth_hash(request, user_obj)
#                         context["success"] = "Password Changed Successfully."
#                         return render(request, 'faculty/faculty_profile_page.html', context)
#                     except Exception as e:
#                         print(e)
#                         context["error"] = "Error in changing password. please try again later."
#                         return render(request, 'faculty/faculty_profile_page.html', context)
#                 else:
#                     context[
#                         "error"] = "Old Password does not match with the one you entered. Please enter correct password."
#                     return render(request, 'faculty/faculty_profile_page.html', context)
#         else:
#             return render(request, 'faculty/faculty_profile_page.html', context)
#     else:
#         context["error"] = "Login first."
#         return render(request, 'home_auth/index.html', context)

def FacultyProfile(request):
    # return render(request, 'faculty_profile_page.html', context={})
    if request.user.is_authenticated:
        faculty_obj = Faculty.objects.get(auth_id=request.user)
        departments = Departments.objects.all()

        context = {
            "base_url": st.BASE_URL,
            "fac_obj": faculty_obj,
            "departments": departments
        }
        context["name"] = str(faculty_obj.name)
        context["email"] = request.user.email
        dept_obj = Departments.objects.get(id=faculty_obj.dept_id.id)
        context["department"] = dept_obj.dept_name

        if request.method == "POST":
            if request.POST.get('name') is not None:
                faculty_obj = Faculty.objects.get(auth_id=request.user)
                departments = Departments.objects.all()
                user_obj = User.objects.get(id=request.user.id)
                name = request.POST.get('name')
                dept_id = request.POST.get('dept')
                department_obj = Departments.objects.get(id=dept_id)
                email = request.POST.get('email')

                faculty_obj.name = name
                faculty_obj.dept_id = department_obj
                faculty_obj.save()

                user_obj.email = email
                user_obj.save()
                request.user = user_obj

                context = {
                    "base_url": st.BASE_URL,
                    "fac_obj": faculty_obj,
                    "departments": departments
                }

                context["success"] = "Profile Updated Successfully"
                context["name"] = str(faculty_obj.name)
                context["email"] = request.user.email
                dept_obj = Departments.objects.get(id=faculty_obj.dept_id.id)
                context["department"] = dept_obj.dept_name
                return render(request, 'faculty/faculty_profile_page.html', context)

            elif request.POST.get('newpwd') is not None:
                oldpwd = request.POST.get('oldpwd')
                newpwd = request.POST.get('newpwd')
                pwd = request.user.password
                if check_password(oldpwd, pwd):
                    try:
                        faculty_obj = Faculty.objects.get(auth_id=request.user)
                        user_obj = User.objects.get(id=request.user.id)
                        user_obj.set_password(str(newpwd))
                        user_obj.save()
                        update_session_auth_hash(request, user_obj)

                        context = {
                            "base_url": st.BASE_URL,
                            "fac_obj": faculty_obj,
                        }

                        context["success"] = "Password Changed Successfully."
                        context["name"] = str(faculty_obj.name)
                        context["email"] = request.user.email
                        dept_obj = Departments.objects.get(id=faculty_obj.dept_id.id)
                        context["department"] = dept_obj.dept_name
                        return render(request, 'faculty/faculty_profile_page.html', context)

                    except Exception as e:
                        context["error"] = "Error in changing password. please try again later."
                        context["name"] = str(faculty_obj.name)
                        context["email"] = request.user.email
                        dept_obj = Departments.objects.get(id=faculty_obj.dept_id.id)
                        context["department"] = dept_obj.dept_name
                        return render(request, 'faculty/faculty_profile_page.html', context)
                else:
                    faculty_obj = Faculty.objects.get(auth_id=request.user)
                    context = {
                        "base_url": st.BASE_URL,
                        "fac_obj": faculty_obj,
                    }

                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    context["name"] = str(faculty_obj.name)
                    context["email"] = request.user.email
                    dept_obj = Departments.objects.get(id=faculty_obj.dept_id.id)
                    context["department"] = dept_obj.dept_name
                    return render(request, 'faculty/faculty_profile_page.html', context)
        else:
            return render(request, 'faculty/faculty_profile_page.html', context)

    else:
        context = {
            "base_url": st.BASE_URL
        }
        context["error"] = "Login to access profile page."
        return render(request, 'home_auth/index.html', context)


def FacultyManageNews(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        news_qs = News.objects.filter(issuing_faculty=fac_obj).order_by('-timestamp')
        context["news_qs"] = news_qs
        return render(request, 'faculty/manage_news.html', context)

    else:
        context["error"] = "Login First"
        return render(request, 'home_auth/index.html', context)


# Faculty Related Views > End

# HOD Related Views > Start
def HodDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        return render(request, 'hod/hod_dashboard.html', context)
    else:
        context["error"] = "login First"
        return render(request, 'home_auth/index.html', context)


def HOD_Profile_View(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        context["email"] = request.user.email
        context["dept"] = fac_obj.dept_id.dept_name
        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                email = request.POST.get('email')
                if name != fac_obj.name or email != request.user.email:
                    fac_obj.name = name
                    fac_obj.save()
                    user_obj = User.objects.get(id=request.user.id)
                    user_obj.email = email
                    user_obj.save()
                    request.user = user_obj
                    context["success"] = "Profile Updated Successfully"
                    context["name"] = fac_obj.name
                    context["email"] = request.user.email
                    context["dept"] = fac_obj.dept_id.dept_name
                    return render(request, 'hod/hod_profile.html', context)

                else:
                    return render(request, 'hod/hod_profile.html', context)

            elif request.POST.get('newpwd') is not None:
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
                        return render(request, 'hod/hod_profile.html', context)
                    except Exception as e:
                        print(e)
                        context["error"] = "Error in changing password. please try again later."
                        return render(request, 'hod/hod_profile.html', context)
                else:
                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'hod/hod_profile.html', context)
        else:
            return render(request, 'hod/hod_profile.html', context)
    else:
        context["error"] = "Login first."
        return render(request, 'home_auth/index.html', context)


def HOD_Manage_department(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        # context["faculty"] = fac_obj
        if fac_obj.hod:
            context["name"] = fac_obj.name
            fac_qs = Faculty.objects.filter(dept_id=fac_obj.dept_id, active=True)
            context["faculties"] = fac_qs
            sub_qs = Subjects.objects.filter(dept_id=fac_obj.dept_id, is_active=True)
            subjects_qs = []
            for s in sub_qs:
                tmp = {}
                tmp["id"] = s.id
                tmp["name"] = s.subject_name
                tmp["code"] = s.subject_code
                tmp["sem"] = s.semester
                subject_to_faculty_qs = Subject_to_Faculty_Mapping.objects.filter(subject_id=s.id)
                tmp["teaching_faculty"] = subject_to_faculty_qs
                subjects_qs.append(tmp)
            context["subjects"] = subjects_qs
            faculty_all = Faculty.objects.filter(active=True)
            context["all_faculty"] = faculty_all
            faculty_dict = {}
            for i in faculty_all:
                faculty_dict[i.id] = {
                    'id': i.id,
                    'name': i.name,
                    'email': i.auth_id.email,
                    'dept_name': i.dept_id.dept_name,
                    'dept_accronym': i.dept_id.accronym
                }

            context['faculty_json'] = json.dumps(faculty_dict)

            if request.method == "POST":
                if request.POST.get('add_Subject_Name') is not None:
                    subject_name = request.POST.get('add_Subject_Name')
                    subject_code = request.POST.get('add_Subject_Code')
                    subject_sem = request.POST.get('add_subject_semester')
                    teaching_faculties_id = request.POST.getlist('add_teaching_faculty')
                    subject_obj, is_created = Subjects.objects.get_or_create(
                        subject_name=subject_name,
                        subject_code=subject_code,
                        semester=subject_sem,
                        dept_id=fac_obj.dept_id,
                    )
                    print(subject_obj, is_created)
                    if is_created:
                        subject_obj.save()
                        for i in teaching_faculties_id:
                            mapping_obj, created = Subject_to_Faculty_Mapping.objects.get_or_create(
                                faculty_id=Faculty.objects.get(id=int(i)),
                                subject_id=subject_obj
                            )

                        context["success"] = str(subject_obj.subject_name) + " has been added successfully"
                        return render(request, 'hod/hod_manage_department.html', context)
                    else:
                        context["error"] = "Subject you are trying to add, already exists"
                        return render(request, 'hod/hod_manage_department.html', context)
                else:
                    context["error"] = "Error in creating subject. Please try again later."
                    return render(request, 'hod/hod_manage_department.html', context)

            else:
                return render(request, 'hod/hod_manage_department.html', context)

        else:
            context["error"] = "You are not authorized to view this page."
            return render(request, 'home_auth/index.html', context)


    else:
        context["error"] = "Log in First"
        return render(request, 'home_auth/index.html', context)


def RemoveFaculty_AJAX(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        if fac_obj.hod:
            if request.method == "GET":
                if request.GET.get('fac_id') is not None:
                    fac_id = request.GET.get('fac_id')
                    fac_obj = Faculty.objects.get(id=int(fac_id))
                    fac_obj.active = False
                    fac_obj.save()
                    context["removed_fac_name"] = fac_obj.name
                    res = json.dumps(context)
                    return HttpResponse(res, status=status.HTTP_200_OK)
                else:
                    context["error"] = "Faculty id not passed."
                    res = json.dumps(context)
                    return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
            else:
                context["error"] = "Error in parsing data."
                res = json.dumps(context)
                return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            context["error"] = "You are not authorized to perform this action."
            res = json.dumps(context)
            return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
    else:
        context["error"] = "Login First"
        res = json.dumps(context)
        return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


def Modify_Subject_AJAX(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        if fac_obj.hod:
            if request.method == "GET":
                if request.GET.get('subject_id') is not None:
                    subject_id = request.GET.get('subject_id')
                    type = request.GET.get('type')
                    if type == 'update':
                        try:
                            subject_obj = Subjects.objects.get(id=int(subject_id), dept_id=fac_obj.dept_id)
                            subject_obj.subject_name = str(request.GET.get('new_subject_name'))
                            subject_obj.subject_code = str(request.GET.get('new_subject_code'))
                            subject_obj.semester = int(request.GET.get('new_subject_sem'))
                            subject_obj.save()
                            new_faculty_list = request.GET.getlist('new_teaching_faculties[]')
                            print(new_faculty_list)
                            Subject_to_Faculty_Mapping.objects.filter(subject_id=subject_obj).delete()
                            for i in new_faculty_list:
                                mapping_obj = Subject_to_Faculty_Mapping.objects.create(
                                    subject_id=subject_obj,
                                    faculty_id=Faculty.objects.get(id=i)
                                )
                                mapping_obj.save()

                            context['subject'] = subject_obj.subject_name
                            res = json.dumps(context)
                            return HttpResponse(res, status=status.HTTP_200_OK)

                        except Exception as e:
                            print(e)
                            context['error'] = "Server Side error. Please contact Developer team."
                            res = json.dumps(context)
                            return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                    elif type == 'delete':
                        try:
                            subject_obj = Subjects.objects.get(id=int(subject_id))
                            subject_obj.is_active = False
                            subject_obj.save()
                            context['subject'] = subject_obj.subject_name
                            res = json.dumps(context)
                            return HttpResponse(res, status=status.HTTP_200_OK)

                        except Exception as e:
                            print(e)
                            context['error'] = "Server Side error. Please contact Developer team."
                            res = json.dumps(context)
                            return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


                else:
                    context["error"] = "Subject id not passed."
                    res = json.dumps(context)
                    return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)
            else:
                context["error"] = "Error in parsing data."
                res = json.dumps(context)
                return HttpResponse(res, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            context["error"] = "You are not authorized to perform this action."
            res = json.dumps(context)
            return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
    else:
        context["error"] = "Login First"
        res = json.dumps(context)
        return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


def HodViewDetailedFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Faculty":
        fac_object = Faculty.objects.get(auth_id=request.user)
        context['name'] = fac_object.name
        context['dept_name'] = fac_object.dept_id.dept_name
        if fac_object.hod:
            dept_faculties = Faculty.objects.filter(dept_id=fac_object.dept_id)
            context["dept_faculties"] = dept_faculties
            subjects_dict = {}
            for i in dept_faculties:
                subjects_dict[i.id] = []
                subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=i.id)
                for j in subject_qs:
                    tmp1 = {
                        "subject_id": j.subject_id.id,
                        "subject_name": j.subject_id.subject_name,
                        "subject_code": j.subject_id.subject_code,
                        "subject_semester": j.subject_id.semester
                    }
                    subjects_dict[i.id].append(tmp1)

            # print(subjects_dict)
            context['fac_subjects'] = json.dumps(subjects_dict)

            if type == "mid-sem":
                questions = Mid_Sem_Feedback_Questions.objects.all()
                context["questions"] = questions
                return render(request, 'hod/Detailed_Feedback/detailed_feedback_mid_sem.html', context)

            elif type == "end-sem":
                questions = End_Sem_Feedback_Questions.objects.all()
                context["questions"] = questions
                return render(request, 'hod/Detailed_Feedback/detailed_feedback_end_sem.html', context)

            else:
                context["error"] = "Page not found."
                return render(request, 'hod/hod_dashboard.html', context)

        else:
            context["error"] = "You are not authorized to view this page."
            return render(request, 'home_auth/index.html', context)

    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


def HodViewAverageFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Faculty":
        fac_object = Faculty.objects.get(auth_id=request.user)
        context['name'] = fac_object.name
        context['dept_name'] = fac_object.dept_id.dept_name
        if fac_object.hod:
            dept_faculties = Faculty.objects.filter(dept_id=fac_object.dept_id)
            context["dept_faculties"] = dept_faculties
            subjects_dict = {}
            for i in dept_faculties:
                subjects_dict[i.id] = []
                subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=i.id)
                for j in subject_qs:
                    tmp1 = {
                        "subject_id": j.subject_id.id,
                        "subject_name": j.subject_id.subject_name,
                        "subject_code": j.subject_id.subject_code,
                        "subject_semester": j.subject_id.semester
                    }
                    subjects_dict[i.id].append(tmp1)

            # print(subjects_dict)
            context['fac_subjects'] = json.dumps(subjects_dict)

            if type == "mid-sem":
                questions = Mid_Sem_Feedback_Questions.objects.all()
                context["questions"] = questions
                return render(request, 'hod/Average_Feedback/average_feedback_mid_sem.html', context)

            elif type == "end-sem":
                questions = End_Sem_Feedback_Questions.objects.all()
                context["questions"] = questions
                return render(request, 'hod/Average_Feedback/average_feedback_end_sem.html', context)

            else:
                context["error"] = "Page not found."
                return render(request, 'hod/hod_dashboard.html', context)

        else:
            context["error"] = "You are not authorized to view this page."
            return render(request, 'home_auth/index.html', context)

    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


# HOD Related Views > End

# Views for ajax related to feedbacks > Start

def GetAverageFeedback(request):
    if request.user.is_authenticated and (request.user.getRole == "Faculty" or request.user.getRole == "Principal"):
        if request.GET.get('fac_id') is not None:
            type = request.GET.get('type')
            term = int(request.GET.get('term'))
            if (term == 0):
                semester_list = [1, 3, 5, 7]
            else:
                semester_list = [2, 4, 6, 8]

            year = int(request.GET.get('year'))
            faculty_obj = Faculty.objects.get(id=int(request.GET.get('fac_id')))
            if type == "mid":
                feedback_qs = Mid_Sem_Feedback_Answers.objects.filter(faculty_id=faculty_obj,
                                                                      semester__in=semester_list, timestamp__year=year)
                rating_list = serialize_feedback(feedback_qs=feedback_qs, faculty_obj=faculty_obj,
                                                 semester_list=semester_list)
                print(rating_list)
                try:
                    data = {
                        "ratings": rating_list,
                        "date": str(feedback_qs.latest().timestamp.strftime("%d %B, %Y %I:%M %p"))
                    }

                except Mid_Sem_Feedback_Answers.DoesNotExist:
                    data = {
                        "ratings": rating_list,
                        "date": str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
                    }

                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_200_OK)

            elif type == "end":
                feedback_qs = End_Sem_Feedback_Answers.objects.filter(faculty_id=faculty_obj,
                                                                      semester__in=semester_list, timestamp__year=year)
                rating_list = serialize_feedback(feedback_qs=feedback_qs, faculty_obj=faculty_obj,
                                                 semester_list=semester_list)
                print(rating_list)
                try:
                    data = {
                        "ratings": rating_list,
                        "date": str(feedback_qs.latest().timestamp.strftime("%d %B, %Y %I:%M %p"))
                    }

                except End_Sem_Feedback_Answers.DoesNotExist:
                    data = {
                        "ratings": rating_list,
                        "date": str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
                    }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_200_OK)

            else:
                data = {
                    "error": "Can not find what you are looking for."
                }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

        else:
            data = {
                "error": "Faculty id not passed."
            }
            res = json.dumps(data)
            return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

    else:
        data = {
            "error": "You are not authorized to access this."
        }
        res = json.dumps(data)
        return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


def GetAllFeedback(request):
    if request.user.is_authenticated and (request.user.getRole == "Faculty" or request.user.getRole == "Principal"):
        if request.GET.get('fac_id') is not None or request.GET.get('sub_id') is not None:
            type = request.GET.get('type')
            term = int(request.GET.get('term'))
            if (term == 0):
                semester_list = [1, 3, 5, 7]
            else:
                semester_list = [2, 4, 6, 8]

            year = int(request.GET.get('year'))
            faculty_obj = Faculty.objects.get(id=int(request.GET.get('fac_id')))
            subject_obj = Subjects.objects.get(id=int(request.GET.get('sub_id')))
            if type == "mid":
                feedback_qs = Mid_Sem_Feedback_Answers.objects.filter(faculty_id=faculty_obj, subject_id=subject_obj,
                                                                      semester__in=semester_list, timestamp__year=year)
                feedback_list = []
                for i in feedback_qs:
                    tmp = {
                        'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p")),
                        'q1': i.Q1, 'q2': i.Q2, 'q3': i.Q3, 'q4': i.Q4, 'q5': i.Q5,
                        'q6': i.Q6, 'q7': i.Q7, 'q8': i.Q8, 'q9': i.Q9, 'q10': i.Q10,
                        'remark': i.remarks
                    }
                    feedback_list.append(tmp)

                data = {
                    'feedback_list': feedback_list
                }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_200_OK)

            elif type == "end":
                feedback_qs = End_Sem_Feedback_Answers.objects.filter(faculty_id=faculty_obj, subject_id=subject_obj,
                                                                      semester__in=semester_list, timestamp__year=year)
                feedback_list = []
                for i in feedback_qs:
                    tmp = {
                        'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p")),
                        'q1': i.Q1, 'q2': i.Q2, 'q3': i.Q3, 'q4': i.Q4, 'q5': i.Q5,
                        'q6': i.Q6, 'q7': i.Q7, 'q8': i.Q8, 'q9': i.Q9, 'q10': i.Q10,
                        'remark': i.remarks
                    }
                    feedback_list.append(tmp)

                data = {
                    'feedback_list': feedback_list
                }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_200_OK)

            else:
                data = {
                    "error": "Can not find what you are looking for."
                }
                res = json.dumps(data)
                return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

        else:
            data = {
                "error": "Faculty id not passed."
            }
            res = json.dumps(data)
            return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

    else:
        data = {
            "error": "You are not authorized to access this."
        }
        res = json.dumps(data)
        return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)


# Views for ajax related to feedbacks > End

# Principal Related Views > Start
def PrincipalDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        principal_obj = Principal.objects.get(auth_id=request.user)
        dept_qs = Departments.objects.all()
        context["departments"] = dept_qs
        context["name"] = principal_obj.name
        committee_qs = Committees.objects.all()
        committee_list = []
        for i in committee_qs:
            tmp = {
                'id': i.id,
                'name': i.committee_name,
                'chairperson': i.chairperson.name,
                'members': Committee_to_Members_Mapping.objects.filter(committee_id=i).count()
            }
            committee_list.append(tmp)
        context["committees"] = committee_list
        return render(request, 'principal/principal_dashboard.html', context)
    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'home_auth/index.html', context)


def ManageCommitteesView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        principal_obj = Principal.objects.get(auth_id=request.user)
        context["name"] = principal_obj.name
        committee_qs = Committees.objects.all()
        context["committees"] = committee_qs
        faculty_qs = Faculty.objects.all()
        context["faculties"] = faculty_qs

        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                details = request.POST.get('details')
                chairperson = request.POST.get('chairperson')
                try:
                    obj = Committees.objects.create(
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
        context["error"] = "Login first to access dashboard."
        return render(request, 'home_auth/index.html', context)


def EditCommittees(request):
    if request.user.is_authenticated:
        if request.user.getRole == "Principal":
            if request.GET.get('committee_id') is not None:
                committee_id = request.GET.get('committee_id')
                action = request.GET.get('action')
                if action == 'update':
                    try:
                        committee_obj = Committees.objects.get(id=int(committee_id))
                        print(committee_obj)
                        committee_obj.committee_name = request.GET.get('committee_name')
                        committee_obj.committee_details = request.GET.get('committee_details')
                        committee_obj.chairperson = Faculty.objects.get(id=int(request.GET.get('chairperson_id')))
                        committee_obj.save()
                        context = {
                            'committee': committee_obj.committee_name
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_200_OK)

                    except Exception as e:
                        print(e)
                        context = {
                            'error': "Server Side error. Please contact Developer team."
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                elif action == 'delete':
                    try:
                        committee_obj = Committees.objects.get(id=int(committee_id))
                        name = committee_obj.committee_name
                        committee_obj.delete()
                        context = {
                            'committee': name
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_200_OK)

                    except Exception as e:
                        print(e)
                        context = {
                            'error': "Server Side error. Please contact Developer team."
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                else:
                    context = {
                        'error': "Error in parsing data."
                    }
                    res = json.dumps(context)
                    return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

            else:
                context = {
                    'error': "Error in parsing data."
                }
                res = json.dumps(context)
                return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

        else:
            context = {
                'error': "You are not authorized to perform this action."
            }
            res = json.dumps(context)
            return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
    else:
        context = {
            'error': "Login First"
        }
        res = json.dumps(context)
        return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)


def ManageDepartmentView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_obj = Principal.objects.get(auth_id=request.user)
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
            except IndexError:
                tmp["hod"] = fac_qs.filter(dept_id=i.id, hod=True)
            print(fac_qs.filter(dept_id=i.id, hod=True))
            dept.append(tmp)
        context["dept"] = dept
        print(dept)
        dept_faculty = {}
        for i in dept_qs:
            dept_faculty[i.id] = []
            faculty_qs = fac_qs.filter(dept_id=i.id)
            for j in faculty_qs:
                tmp = {}
                tmp['faculty_id'] = j.id
                tmp['faculty_name'] = j.name
                dept_faculty[i.id].append(tmp)

        context['dept_faculty'] = json.dumps(dept_faculty)
        context["faculties"] = fac_qs
        return render(request, 'principal/manage_departments.html', context)
    else:
        context["error"] = "You are not authorized to view this page."
        return render(request, 'home_auth/index.html', context)


def EditHOD(request):
    if request.user.is_authenticated:
        if request.user.getRole == "Principal":
            if request.method == "GET":
                old_hod_id = request.GET.get('old_hod')
                new_hod_id = request.GET.get('fac_id')
                try:
                    if (old_hod_id != '-1'):
                        old_hod = Faculty.objects.get(id=int(old_hod_id))
                        old_hod.hod = False
                        old_hod.save()
                        print("Old HOD: ", old_hod)
                        new_hod = Faculty.objects.get(id=int(new_hod_id))
                        print("New HOD: ", new_hod)
                        new_hod.hod = True
                        new_hod.save()
                        context = {
                            'dept': new_hod.dept_id.dept_name
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_200_OK)

                    else:
                        new_hod = Faculty.objects.get(id=int(new_hod_id))
                        print("New HOD: ", new_hod)
                        new_hod.hod = True
                        new_hod.save()
                        context = {
                            'dept': new_hod.dept_id.dept_name
                        }
                        res = json.dumps(context)
                        return HttpResponse(res, status=status.HTTP_200_OK)

                except Exception as e:
                    print(e)
                    context = {
                        'error': "Server Side error. Please contact Developer team."
                    }
                    res = json.dumps(context)
                    return HttpResponse(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            else:
                context = {
                    'error': "Error in parsing data."
                }
                res = json.dumps(context)
                return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)

        else:
            context = {
                'error': "You are not authorized to change Head of the department."
            }
            res = json.dumps(context)
            return HttpResponse(res, status=status.HTTP_401_UNAUTHORIZED)
    else:
        context = {
            'error': "Login First"
        }
        res = json.dumps(context)
        return HttpResponse(res, status=status.HTTP_400_BAD_REQUEST)


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
                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'principal/principal_profile_page.html', context)
        else:
            return render(request, 'principal/principal_profile_page.html', context)

    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'home_auth/index.html', context)


def DetailedFeedback(request, id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_object = Principal.objects.get(auth_id=request.user)
        context['name'] = principal_object.name

        try:
            dept_obj = Departments.objects.get(id=id)
        except Departments.DoesNotExist:
            return HttpResponse("404 Page not found.")

        context['dept_name'] = dept_obj.dept_name
        dept_faculties = Faculty.objects.filter(dept_id=dept_obj)
        context["dept_faculties"] = dept_faculties
        subjects_dict = {}
        for i in dept_faculties:
            subjects_dict[i.id] = []
            subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=i.id)
            for j in subject_qs:
                tmp1 = {
                    "subject_id": j.subject_id.id,
                    "subject_name": j.subject_id.subject_name,
                    "subject_code": j.subject_id.subject_code,
                    "subject_semester": j.subject_id.semester
                }
                subjects_dict[i.id].append(tmp1)

        context['fac_subjects'] = json.dumps(subjects_dict)

        Questions_list = {
            'mid': [],
            'end': []
        }
        mid_questions = Mid_Sem_Feedback_Questions.objects.all()
        for i in mid_questions:
            tmp = {
                'question_text': i.question_text
            }
            Questions_list['mid'].append(tmp)

        end_questions = End_Sem_Feedback_Questions.objects.all()
        for i in end_questions:
            tmp = {
                'question_text': i.question_text
            }
            Questions_list['end'].append(tmp)

        print(Questions_list)
        context['question_list'] = json.dumps(Questions_list)
        return render(request, 'principal/detailed_feedback.html', context)

    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


def AverageFeedback(request, id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_obj = Principal.objects.get(auth_id=request.user)
        context['name'] = principal_obj.name

        try:
            dept_obj = Departments.objects.get(id=id)
        except Departments.DoesNotExist:
            return HttpResponse("404 Page not found.")

        context['dept_name'] = dept_obj.dept_name

        dept_faculties = Faculty.objects.filter(dept_id=dept_obj)
        context["dept_faculties"] = dept_faculties
        subjects_dict = {}
        for i in dept_faculties:
            subjects_dict[i.id] = []
            subject_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=i.id)
            for j in subject_qs:
                tmp1 = {
                    "subject_id": j.subject_id.id,
                    "subject_name": j.subject_id.subject_name,
                    "subject_code": j.subject_id.subject_code,
                    "subject_semester": j.subject_id.semester
                }
                subjects_dict[i.id].append(tmp1)

        # print(subjects_dict)
        context['fac_subjects'] = json.dumps(subjects_dict)

        Questions_list = {
            'mid': [],
            'end': []
        }
        mid_questions = Mid_Sem_Feedback_Questions.objects.all()
        for i in mid_questions:
            tmp = {
                'question_text': i.question_text
            }
            Questions_list['mid'].append(tmp)

        end_questions = End_Sem_Feedback_Questions.objects.all()
        for i in end_questions:
            tmp = {
                'question_text': i.question_text
            }
            Questions_list['end'].append(tmp)

        print(Questions_list)
        context['question_list'] = json.dumps(Questions_list)
        return render(request, 'principal/average feedback.html', context)

    else:
        context["error"] = "Log in First."
        return render(request, 'home_auth/index.html', context)


def DownloadDetailedReport(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        if request.POST.get('type') is not None:
            type = request.POST.get('type')
            if (type == "0"):
                fb_type = "mid"
            else:
                fb_type = "end"
            return DownloadDetailedFeedback(request, type=fb_type)
    else:
        return render(request, 'principal/detailed_feedback.html', context)


def DownloadAverageReport(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        if request.POST.get('type') is not None:
            type = request.POST.get('type')
            if (type == "0"):
                fb_type = "mid"
            else:
                fb_type = "end"
            return DownloadAverageFeedback(request, type=fb_type)
    else:
        return render(request, 'principal/detailed_feedback.html', context)


# Principal Related Views > End

# Committee Related Views > Start
def CommitteeChairpersonDashboard(request, com_id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        committee_obj = Committees.objects.get(id=com_id)
        context["committee_name"] = committee_obj.committee_name
        context["committee_id"] = committee_obj.id
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        if committee_obj.chairperson != fac_obj:
            return HttpResponse("You are not authorized to view this page.")

        if request.POST.get('complaint_id') is not None:
            complaint_id = request.POST.get('complaint_id')
            complaint_obj = Complaints.objects.get(id=int(complaint_id))
            status = request.POST.get('status')
            if status == "Pending":
                action = request.POST.get('action')
                complaint_obj.status = "Closed"
                complaint_obj.save()

                solution_obj = Complaints_Solutions.objects.create(
                    complaint_id=complaint_obj,
                    reacting_faculty=fac_obj,
                    action=action
                )
                solution_obj.save()
                context["success"] = "Action has been taken against " + str(
                    complaint_obj.student_id.first_name) + " " + str(
                    complaint_obj.student_id.last_name) + "'s complaint."

            elif status == "Re-opened":
                comment = request.POST.get('comment')
                complaint_obj.status = "Closed"
                complaint_obj.save()

                solution_obj = Complaints_Solutions.objects.create(
                    complaint_id=complaint_obj,
                    reacting_faculty=fac_obj,
                    reopen_count=int(complaint_obj.reopened_count),
                    action=comment
                )
                solution_obj.save()
                context["success"] = "Action has been taken against " + str(
                    complaint_obj.student_id.first_name) + " " + str(
                    complaint_obj.student_id.last_name) + "'s complaint."

        complaints_qs = Complaints.objects.filter(committee_id=committee_obj)
        # ===================== For pending Complaints ==================================
        pending_qs = complaints_qs.filter(status="Pending").filter(revoked=False).order_by('-timestamp')
        pending_count = pending_qs.count()
        if pending_count == 0:
            context["no_pending_complaints"] = True

        else:
            context["no_pending_complaints"] = False

        context["pending_count"] = pending_count

        pending_dict = []
        for i in pending_qs:
            tmp = {
                'id': i.id,
                'student_name': str(i.student_id.first_name) + " " + str(i.student_id.last_name),
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            pending_dict.append(tmp)

        context["pending_complaints"] = pending_dict

        # ===================== For Re-opened Complaints ==================================
        reopened_qs = complaints_qs.filter(status="Re-Opened").filter(revoked=False).order_by('-timestamp')
        reopened_count = reopened_qs.count()
        if reopened_count == 0:
            context["no_reopened_complaints"] = True

        else:
            context["no_reopened_complaints"] = False

        context["reopened_count"] = reopened_count

        reopened_dict = []
        for i in reopened_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': student_name,
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)
                    try:
                        faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': faculty_response.reacting_faculty.name,
                            'comment': faculty_response.action,
                            'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                            'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)

                    except Complaints_Solutions.DoesNotExist:
                        pass

                j += 1

            reopened_dict.append(tmp)
        # print(reopened_dict)

        context["reopened_complaints"] = reopened_dict
        # ===================== For Closed Complaints =====================================
        closed_qs = complaints_qs.filter(status="Closed").filter(revoked=False).order_by('-timestamp')
        closed_count = closed_qs.count()
        if closed_count == 0:
            context["no_closed_complaints"] = True

        else:
            context["no_closed_complaints"] = False

        context["closed_count"] = closed_count

        closed_dict = []
        for i in closed_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': student_name,
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)

                    faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': faculty_response.reacting_faculty.name,
                        'comment': faculty_response.action,
                        'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                        'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                j += 1

            closed_dict.append(tmp)
        # print(closed_dict)

        context["closed_complaints"] = closed_dict
        # ===================== For Revoked Complaints ====================================
        revoked_qs = complaints_qs.filter(status="Revoked").filter(revoked=True).order_by('-timestamp')
        revoked_count = revoked_qs.count()
        if revoked_count == 0:
            context["no_revoked_complaints"] = True

        else:
            context["no_revoked_complaints"] = False

        context["revoked_count"] = revoked_count

        revoked_dict = []
        for i in revoked_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'revoked_reason': i.revoked_reason,
                'revoked_date': str(i.revoked_date.strftime("%d %B, %Y %I:%M %p")),
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            if actions_count > 0:
                j = 0
                while j <= actions_count:
                    if j < 1:
                        response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': response_obj.reacting_faculty.name,
                            'comment': response_obj.action,
                            'dept': response_obj.reacting_faculty.dept_id.dept_name,
                            'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)
                    else:
                        student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': student_name,
                            'comment': student_response.comments,
                            'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Re-Opened'
                        }
                        tmp["actions"].append(tmp1)
                        try:
                            faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                            tmp1 = {
                                'name': faculty_response.reacting_faculty.name,
                                'comment': faculty_response.action,
                                'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                                'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                                'action': 'Closed'
                            }
                            tmp["actions"].append(tmp1)

                        except Complaints_Solutions.DoesNotExist:
                            pass

                    j += 1
            else:
                tmp["actions"] = []

            revoked_dict.append(tmp)
        # print(revoked_dict)

        context["revoked_complaints"] = revoked_dict

        return render(request, 'committees/chairperson.html', context)
    else:
        context["error"] = "Log in First"
        return render(request, 'home_auth/index.html', context)


def CommitteeMemberDashboard(request, com_id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        committee_obj = Committees.objects.get(id=com_id)
        context["committee_name"] = committee_obj.committee_name
        context["committee_id"] = committee_obj.id
        if request.user.getRole == "Faculty":
            fac_obj = Faculty.objects.get(auth_id=request.user)
            context["name"] = fac_obj.name
            context["role"] = "Faculty"
            try:
                mapping_obj = Committee_to_Members_Mapping.objects.get(committee_id=committee_obj, faculty_id=fac_obj)
            except Committee_to_Members_Mapping.DoesNotExist:
                return HttpResponse("You are not member of this committee")

        elif request.user.getRole == "Principal":
            principal_obj = Principal.objects.get(auth_id=request.user)
            context["name"] = principal_obj.name
            context["role"] = "Principal"

        else:
            return HttpResponse("You are not authorized to view this page.")

        if request.POST.get('complaint_id') is not None:
            complaint_id = request.POST.get('complaint_id')
            complaint_obj = Complaints.objects.get(id=int(complaint_id))
            status = request.POST.get('status')
            if status == "Pending":
                action = request.POST.get('action')
                complaint_obj.status = "Closed"
                complaint_obj.save()

                solution_obj = Complaints_Solutions.objects.create(
                    complaint_id=complaint_obj,
                    reacting_faculty=fac_obj,
                    action=action
                )
                solution_obj.save()
                context["success"] = "Action has been taken against " + str(
                    complaint_obj.student_id.first_name) + " " + str(
                    complaint_obj.student_id.last_name) + "'s complaint."

            elif status == "Re-opened":
                comment = request.POST.get('comment')
                complaint_obj.status = "Closed"
                complaint_obj.save()

                solution_obj = Complaints_Solutions.objects.create(
                    complaint_id=complaint_obj,
                    reacting_faculty=fac_obj,
                    reopen_count=int(complaint_obj.reopened_count),
                    action=comment
                )
                solution_obj.save()
                context["success"] = "Action has been taken against " + str(
                    complaint_obj.student_id.first_name) + " " + str(
                    complaint_obj.student_id.last_name) + "'s complaint."

        complaints_qs = Complaints.objects.filter(committee_id=committee_obj)
        # ===================== For pending Complaints ==================================
        pending_qs = complaints_qs.filter(status="Pending").filter(revoked=False).order_by('-timestamp')
        pending_count = pending_qs.count()
        if pending_count == 0:
            context["no_pending_complaints"] = True

        else:
            context["no_pending_complaints"] = False

        context["pending_count"] = pending_count

        pending_dict = []
        for i in pending_qs:
            tmp = {
                'id': i.id,
                'student_name': str(i.student_id.first_name) + " " + str(i.student_id.last_name),
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            pending_dict.append(tmp)

        context["pending_complaints"] = pending_dict

        # ===================== For Re-opened Complaints ==================================
        reopened_qs = complaints_qs.filter(status="Re-Opened").filter(revoked=False).order_by('-timestamp')
        reopened_count = reopened_qs.count()
        if reopened_count == 0:
            context["no_reopened_complaints"] = True

        else:
            context["no_reopened_complaints"] = False

        context["reopened_count"] = reopened_count

        reopened_dict = []
        for i in reopened_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': student_name,
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)
                    try:
                        faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': faculty_response.reacting_faculty.name,
                            'comment': faculty_response.action,
                            'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                            'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)

                    except Complaints_Solutions.DoesNotExist:
                        pass

                j += 1

            reopened_dict.append(tmp)
        # print(reopened_dict)

        context["reopened_complaints"] = reopened_dict
        # ===================== For Closed Complaints =====================================
        closed_qs = complaints_qs.filter(status="Closed").filter(revoked=False).order_by('-timestamp')
        closed_count = closed_qs.count()
        if closed_count == 0:
            context["no_closed_complaints"] = True

        else:
            context["no_closed_complaints"] = False

        context["closed_count"] = closed_count

        closed_dict = []
        for i in closed_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            j = 0
            while j <= actions_count:
                # print("yes")
                if j < 1:
                    response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': response_obj.reacting_faculty.name,
                        'comment': response_obj.action,
                        'dept': response_obj.reacting_faculty.dept_id.dept_name,
                        'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                else:
                    student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': student_name,
                        'comment': student_response.comments,
                        'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Re-Opened'
                    }
                    tmp["actions"].append(tmp1)

                    faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                    tmp1 = {
                        'name': faculty_response.reacting_faculty.name,
                        'comment': faculty_response.action,
                        'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                        'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                        'action': 'Closed'
                    }
                    tmp["actions"].append(tmp1)
                j += 1

            closed_dict.append(tmp)
        # print(closed_dict)

        context["closed_complaints"] = closed_dict
        # ===================== For Revoked Complaints ====================================
        revoked_qs = complaints_qs.filter(status="Revoked").filter(revoked=True).order_by('-timestamp')
        revoked_count = revoked_qs.count()
        if revoked_count == 0:
            context["no_revoked_complaints"] = True

        else:
            context["no_revoked_complaints"] = False

        context["revoked_count"] = revoked_count

        revoked_dict = []
        for i in revoked_qs:
            student_name = str(i.student_id.first_name) + " " + str(i.student_id.last_name)
            tmp = {
                'id': i.id,
                'student_name': student_name,
                'student_enrl': i.student_id.enrollment_no,
                'student_dept': i.student_id.dept_id.dept_name,
                'description': i.complaint_details,
                'reopened_count': i.reopened_count,
                'revoked_reason': i.revoked_reason,
                'revoked_date': str(i.revoked_date.strftime("%d %B, %Y %I:%M %p")),
                'date': str(i.timestamp.strftime("%d %B, %Y %I:%M %p"))
            }
            actions_count = i.reopened_count
            tmp["actions"] = []
            if actions_count > 0:
                j = 0
                while j <= actions_count:
                    if j < 1:
                        response_obj = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': response_obj.reacting_faculty.name,
                            'comment': response_obj.action,
                            'date': response_obj.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'dept': response_obj.reacting_faculty.dept_id.dept_name,
                            'action': 'Closed'
                        }
                        tmp["actions"].append(tmp1)
                    else:
                        student_response = Complaint_Reopen_comments.objects.get(complaint_id=i, reopen_count=j)
                        tmp1 = {
                            'name': student_name,
                            'comment': student_response.comments,
                            'date': student_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                            'action': 'Re-Opened'
                        }
                        tmp["actions"].append(tmp1)
                        try:
                            faculty_response = Complaints_Solutions.objects.get(complaint_id=i, reopen_count=j)
                            tmp1 = {
                                'name': faculty_response.reacting_faculty.name,
                                'comment': faculty_response.action,
                                'dept': faculty_response.reacting_faculty.dept_id.dept_name,
                                'date': faculty_response.timestamp.strftime("%d %B, %Y %I:%M %p"),
                                'action': 'Closed'
                            }
                            tmp["actions"].append(tmp1)

                        except Complaints_Solutions.DoesNotExist:
                            pass

                    j += 1
            else:
                tmp["actions"] = []

            revoked_dict.append(tmp)
        # print(revoked_dict)

        context["revoked_complaints"] = revoked_dict

        return render(request, 'committees/members.html', context)
    else:
        context["error"] = "Log in First"
        return render(request, 'home_auth/index.html', context)


def CommitteeViewMembers(request, com_id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        committee_obj = Committees.objects.get(id=com_id)
        context["committee_name"] = committee_obj.committee_name
        context["committee_id"] = committee_obj.id
        context["chairperson_name"] = committee_obj.chairperson.name
        context["chairperson_dept"] = committee_obj.chairperson.dept_id.dept_name
        if request.user.getRole == "Faculty":
            fac_obj = Faculty.objects.get(auth_id=request.user)
            context["name"] = fac_obj.name
            try:
                mapping_obj = Committee_to_Members_Mapping.objects.get(committee_id=committee_obj, faculty_id=fac_obj)
            except Committee_to_Members_Mapping.DoesNotExist:
                return HttpResponse("You are not member of this committee")

        elif request.user.getRole == "Principal":
            principal_obj = Principal.objects.get(auth_id=request.user)
            context["name"] = principal_obj.name

        else:
            return HttpResponse("You are not authorized to view this page.")

        members_qs = Committee_to_Members_Mapping.objects.filter(committee_id=committee_obj)
        context["members"] = members_qs

        return render(request, 'committees/view_members.html', context)

    else:
        context["error"] = "Login First"
        return render(request, 'home_auth/index.html', context)


def CommitteeManageMembers(request, com_id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        committee_obj = Committees.objects.get(id=com_id)
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name

        if committee_obj.chairperson != fac_obj:
            return HttpResponse("You are not authorized to view this page.")

        if request.method == "POST":
            if request.POST.get('faculty_id') is not None:
                fac_id = request.POST.get('faculty_id')
                print(fac_id)
                fac_member_obj = Faculty.objects.get(id=int(fac_id))
                print(fac_member_obj)
                mapping_obj = Committee_to_Members_Mapping.objects.get(committee_id=committee_obj,
                                                                       faculty_id=fac_member_obj)
                print(mapping_obj)
                mapping_obj.delete()

                context["success"] = fac_member_obj.name + " has been removed successfully."

            if request.POST.get('member') is not None:
                member_id = request.POST.get('member')
                try:
                    mapping_obj, is_created = Committee_to_Members_Mapping.objects.get_or_create(
                        committee_id=committee_obj,
                        faculty_id=Faculty.objects.get(id=int(member_id))
                    )
                    if is_created:
                        mapping_obj.save()
                        context["success"] = mapping_obj.faculty_id.name + " has been successfully added as member."
                    else:
                        context["success"] = 'Selected faculty is already member of this committee.'

                except Exception as e:
                    print(e)
                    context["error"] = "Server Error has been occured."

        context["committee_name"] = committee_obj.committee_name
        context["committee_id"] = committee_obj.id
        context["chairperson_name"] = committee_obj.chairperson.name
        context["chairperson_dept"] = committee_obj.chairperson.dept_id.dept_name
        context["chairperson_id"] = committee_obj.chairperson.id

        all_dept = Departments.objects.all()
        dept_faculties = []
        for i in all_dept:
            tmp = {
                'name': i.dept_name,
                'faculties': Faculty.objects.filter(dept_id=i)
            }
            dept_faculties.append(tmp)
        print(dept_faculties)
        context['dept_faculties'] = dept_faculties

        members_qs = Committee_to_Members_Mapping.objects.filter(committee_id=committee_obj)
        context["members"] = members_qs

        return render(request, 'committees/manage_members.html', context)

    else:
        context["error"] = "Login First"
        return render(request, 'home_auth/index.html', context)


# Committee Related Views > End

# Download Report Views > Start
def DownloadDetailedFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('faculty') is not None:
                fac_obj = Faculty.objects.get(id=int(request.POST.get('faculty')))
                term = int(request.POST.get('term'))
                if term == 0:
                    term_type = "ODD"
                    semester_list = [1, 3, 5, 7]
                else:
                    term_type = "Even"
                    semester_list = [2, 4, 6, 8]

                year = int(request.POST.get('year'))

                subject_obj = Subjects.objects.get(id=int(request.POST.get('subject')))
                if type == "mid":
                    fb_type = "Mid"
                    question_qs = Mid_Sem_Feedback_Questions.objects.all()
                    question_count = question_qs.count()
                    feedback_qs = Mid_Sem_Feedback_Answers.objects.filter(
                        faculty_id=fac_obj,
                        subject_id=subject_obj,
                        semester__in=semester_list,
                        timestamp__year=year
                    )

                elif type == "end":
                    fb_type = "End"
                    question_qs = End_Sem_Feedback_Questions.objects.all()
                    question_count = question_qs.count()
                    feedback_qs = End_Sem_Feedback_Answers.objects.filter(
                        faculty_id=fac_obj,
                        subject_id=subject_obj,
                        semester__in=semester_list,
                        timestamp__year=year
                    )

                serialized_feedback = serialize_detailed_feedback(feedback_qs=feedback_qs)

                # ====================== PDF Generation ===================================
                pdfname = str(subject_obj.subject_name)
                pdfname = pdfname.replace(" ", "_")
                response = HttpResponse(content_type='application/pdf')
                response[
                    'Content-Disposition'] = 'attachment; filename=' + pdfname + '_' + fb_type + '_Semester_Detailed_Feedback.pdf'

                elements = []

                doc = SimpleDocTemplate(response, rightMargin=inch / 4,
                                        leftMargin=inch / 4,
                                        topMargin=inch / 2,
                                        bottomMargin=inch / 4,
                                        pagesize=A4)

                path_to_file = os.getcwd() + "/logo.jpg"

                for k in serialized_feedback:

                    text1 = "Government Engineering College, Bhavnagar"
                    text2 = fb_type + " Semester Feedback Report"
                    text3 = "Term: " + term_type + " " + str(year)
                    text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
                    text5 = str(fac_obj.dept_id.dept_name) + " Department"
                    text6 = fac_obj.name
                    text7 = "Subject Name: " + subject_obj.subject_name + " (" + subject_obj.subject_code + ")"
                    text8 = "Semester: " + str(subject_obj.semester)
                    text9 = "Date of Feedback: " + str(k['date'])

                    d = Drawing(400, 200)
                    d.add(Image(0, 120, 100, 100, path_to_file))
                    d.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
                    d.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
                    d.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
                    d.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
                    d.add(Line(0, 90, 550, 90))
                    d.add(String(150, 65, text5, fontSize=18, fillColor=colors.black))
                    d.add(String(30, 35, text6, fontSize=12, fillColor=colors.black))
                    d.add(String(30, 20, text7, fontSize=12, fillColor=colors.black))
                    d.add(String(380, 20, text8, fontSize=12, fillColor=colors.black))
                    d.add(String(22, -45, text9, fontSize=12, fillColor=colors.black))

                    elements.append(d)
                    elements.append(Spacer(500, 50))

                    fl = [["Sr No", "Questions", "Feedback"]]
                    for i in range(1, question_count + 1):
                        index = "q" + str(i)
                        ft = []
                        ft.append(i)
                        ft.append(question_qs[i - 1].question_text)
                        ft.append(k[index])
                        fl.append(ft)

                    # fl.append([11, 'Remarks', l[k][10]])

                    # data = fl
                    # table = Table(data, 12 * [0.5 * inch])
                    table = Table(fl)

                    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                               ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                               ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                               ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                               ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                               ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                                               ]))
                    table._argW[0] = 1.0 * inch
                    table._argW[1] = 4.0 * inch
                    table._argW[2] = 2.0 * inch

                    table._argH[0] = 0.5 * inch
                    for i in range(1, question_count + 1):
                        table._argH[i] = 0.4 * inch

                    # table._argH[1] = 0.4 * inch
                    # table._argH[2] = 0.4 * inch
                    # table._argH[3] = 0.4 * inch
                    # table._argH[4] = 0.4 * inch
                    # table._argH[5] = 0.4 * inch
                    # table._argH[6] = 0.4 * inch
                    # table._argH[7] = 0.4 * inch
                    # table._argH[8] = 0.4 * inch
                    # table._argH[9] = 0.4 * inch
                    # table._argH[10] = 0.4 * inch
                    # table._argH[11] = 0.4 * inch

                    elements.append(table)

                    drawing_for_remarks = Drawing(400, 200)
                    drawing_for_remarks.add(
                        String(22, 170, "Remarks: " + str(k['remark']), fontSize=12, fillColor=colors.black))

                    drawing_for_remarks.add(
                        String(22, 100, "Note: All the feedback given are out of 5.", fontSize=12,
                               fillColor=colors.black))

                    elements.append(drawing_for_remarks)

                    elements.append(PageBreak())

                doc.build(elements)
                return response


    else:
        context["error"] = "Log in First"
        return render(request, 'home_auth/index.html', context)


def DownloadAverageFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST.get('faculty') is not None:
                fac_obj = Faculty.objects.get(id=int(request.POST.get('faculty')))
                term = int(request.POST.get('term'))
                if term == 0:
                    term_type = "ODD"
                    semester_list = [1, 3, 5, 7]
                else:
                    term_type = "Even"
                    semester_list = [2, 4, 6, 8]

                year = int(request.POST.get('year'))

                subject_obj = Subjects.objects.get(id=int(request.POST.get('subject')))
                if type == "mid":
                    fb_type = "Mid"
                    question_qs = Mid_Sem_Feedback_Questions.objects.all()
                    question_count = question_qs.count()
                    feedback_qs = Mid_Sem_Feedback_Answers.objects.filter(
                        faculty_id=fac_obj,
                        subject_id=subject_obj,
                        semester__in=semester_list,
                        timestamp__year=year
                    )
                    rating_insights = ratings_detailed(feedback_qs=feedback_qs)

                elif type == "end":
                    fb_type = "End"
                    question_qs = End_Sem_Feedback_Questions.objects.all()
                    question_count = question_qs.count()
                    feedback_qs = End_Sem_Feedback_Answers.objects.filter(
                        faculty_id=fac_obj,
                        subject_id=subject_obj,
                        semester__in=semester_list,
                        timestamp__year=year
                    )
                    rating_insights = ratings_detailed(feedback_qs=feedback_qs)

                # Got dictionary of question wise average rating as well as count.
                questionwise_ratings = serialize_feedback_subject(feedback_qs=feedback_qs)

                # =========== PDF Generation ===============================================
                ##################################################################################################################

                pdfname1 = "Temp1"

                response1 = HttpResponse(content_type='application/pdf')
                response1['Content-Disposition'] = 'attachment; filename=' + pdfname1

                elements1 = []
                doc1 = SimpleDocTemplate(response1, rightMargin=inch / 4,
                                         leftMargin=inch / 4,
                                         topMargin=inch / 2,
                                         bottomMargin=inch / 4,
                                         pagesize=A4)

                path_to_file = os.getcwd() + "/logo.jpg"

                text1 = "Government Engineering College, Bhavnagar"
                text2 = fb_type + " Semester Feedback Report"
                text3 = "Term: " + term_type + " " + str(year)
                text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
                text5 = str(fac_obj.dept_id.dept_name) + " Department"
                text6 = fac_obj.name
                text7 = "Subject Name: " + subject_obj.subject_name + " (" + subject_obj.subject_code + ")"
                text8 = "Semester: " + str(subject_obj.semester)
                text9 = "Total Feedback: " + str(questionwise_ratings["count"])

                d = Drawing(400, 200)
                d.add(Image(0, 120, 100, 100, path_to_file))
                d.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
                d.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
                d.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
                d.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
                d.add(Line(0, 90, 550, 90))
                d.add(String(150, 65, text5, fontSize=18, fillColor=colors.black))
                d.add(String(30, 35, text6, fontSize=12, fillColor=colors.black))
                d.add(String(30, 20, text7, fontSize=12, fillColor=colors.black))
                d.add(String(380, 20, text8, fontSize=12, fillColor=colors.black))
                d.add(String(22, -45, text9, fontSize=12, fillColor=colors.black))

                elements1.append(d)

                drawing = Drawing(400, 200)
                drawing.vAlign = 'CENTER'

                data_list = []
                label_list = []
                for i in range(1, question_count + 1):
                    index = "Q" + str(i)
                    data_list.append(questionwise_ratings[index])
                    label_list.append(("Question : " + str(i)))

                data = []
                data.append(tuple(data_list))
                print(data)
                bc = VerticalBarChart()
                bc.x = 28
                bc.y = -120
                bc.height = 250
                bc.width = 500
                bc.data = data
                bc.bars[0].fillColor = colors.aqua
                bc.strokeColor = colors.black
                bc.valueAxis.valueMin = 0
                bc.valueAxis.valueMax = 5.0
                bc.valueAxis.valueStep = 0.5
                bc.categoryAxis.labels.boxAnchor = 'ne'
                bc.categoryAxis.labels.dx = 8
                bc.categoryAxis.labels.dy = -2
                bc.categoryAxis.labels.angle = 30
                bc.categoryAxis.categoryNames = label_list
                bc.barLabels.angle = 0
                bc.barLabels.boxAnchor = 's'
                bc.barLabelFormat = DecimalFormatter(2)
                drawing.add(bc)

                elements1.append(drawing)

                elements1.append(PageBreak())

                ##################################################################################################################

                pdfname2 = "Temp1"
                response2 = HttpResponse(content_type='application/pdf')
                response2['Content-Disposition'] = 'attachment; filename=' + pdfname2

                elements2 = []
                doc2 = SimpleDocTemplate(response2, rightMargin=inch / 4,
                                         leftMargin=inch / 4,
                                         topMargin=inch / 2,
                                         bottomMargin=inch / 4,
                                         pagesize=A4)

                path_to_file = os.getcwd() + "/logo.jpg"

                text1 = "Government Engineering College, Bhavnagar"
                text2 = fb_type + " Semester Feedback Report"
                text3 = "Term: " + term_type + " " + str(year)
                text4 = "Date: " + str(datetime.datetime.now().strftime("%d %B, %Y %I:%M %p"))
                text5 = "Total Feedback: " + str(questionwise_ratings["count"])

                d2 = Drawing(400, 200)
                d2.add(Image(0, 120, 100, 100, path_to_file))
                d2.add(String(120, 190, text1, fontSize=20, fillColor=colors.black))
                d2.add(String(170, 150, text2, fontSize=18, fillColor=colors.black))
                d2.add(String(30, 110, text3, fontSize=14, fillColor=colors.black))
                d2.add(String(370, 110, text4, fontSize=14, fillColor=colors.black))
                d2.add(Line(0, 90, 550, 90))
                d2.add(String(30, 70, text5, fontSize=12, fillColor=colors.black))

                elements2.append(d2)

                elements2.append(Spacer(550, -50))

                fl = [["Sr No", "Questions", "Feedback"]]
                for i in range(question_count):
                    index = "Q" + str(i + 1)
                    dpie = Drawing(200, 100)
                    pc = Pie()
                    pc.x = 65
                    pc.y = 15
                    pc.width = 70
                    pc.height = 70
                    pc.sideLabels = 1
                    pc.data = [rating_insights[index][1], rating_insights[index][2], rating_insights[index][3],
                               rating_insights[index][4], rating_insights[index][5]]
                    pc.labels = ['1', '2', '3', '4', '5']
                    pc.slices.strokeWidth = 0.5
                    pc.slices[0].fillColor = colors.red
                    pc.slices[1].fillColor = colors.blue
                    pc.slices[2].fillColor = colors.gray
                    pc.slices[3].fillColor = colors.yellow
                    pc.slices[4].fillColor = colors.green
                    dpie.add(pc)
                    legend = Legend()
                    legend.alignment = 'right'
                    legend.x = 160
                    legend.y = 90
                    legend.columnMaximum = 5
                    legend.dxTextSpace = 4
                    n = len(pc.data)
                    legend.colorNamePairs = [(pc.slices[i].fillColor, (pc.labels[i], ': ' + '%0.2f' % pc.data[i] + '%'))
                                             for i in
                                             range(n)]
                    dpie.add(legend)

                    ft = []
                    ft.append(i + 1)
                    ft.append(question_qs[i].question_text)
                    ft.append([dpie])
                    fl.append(ft)

                tbdata = fl

                table = Table(tbdata)

                table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.white),
                                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                           ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                                           ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                                           ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                           ('BACKGROUND', (0, -1), (-1, -1), colors.white),
                                           ]))
                table._argW[0] = 0.6 * inch
                table._argW[1] = 3.5 * inch
                table._argW[2] = 3.3 * inch

                table._argH[0] = 0.35 * inch
                for i in range(1, question_count + 1):
                    table._argH[i] = 1.6 * inch

                table.spaceBefore = 0

                elements2.append(table)

                ##################################################################################################################

                pdfname3 = str(subject_obj.subject_name)
                pdfname3 = pdfname3.replace(" ", "_")
                response3 = HttpResponse(content_type='application/pdf')
                response3[
                    'Content-Disposition'] = 'attachment; filename=' + pdfname3 + '_' + fb_type + '_Semester_Average_Feedback.pdf'
                elements3 = []

                doc3 = SimpleDocTemplate(response3, rightMargin=inch / 4,
                                         leftMargin=inch / 4,
                                         topMargin=inch / 2,
                                         bottomMargin=inch / 4,
                                         pagesize=A4)

                for i in elements1:
                    elements3.append(i)

                for i in elements2:
                    elements3.append(i)

                doc3.build(elements3)

                return response3

    else:
        context["error"] = "Log in First"
        return render(request, 'home_auth/index.html', context)

# Download Report Views > End
