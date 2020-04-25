import datetime
import json
from base64 import b64encode, b64decode
from itertools import chain

from .utils import *
from email.utils import decode_params
from io import BytesIO
import traceback

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


# TODO : There are some pending changes in change password templates.
def ChangePasswordView(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.method == "GET":
        if request.GET.get('email') is not None:
            raw_email = str(request.GET.get('email'))
            email = b64decode(raw_email.encode()).decode('utf-8')
            request.session["email"] = email
            return render(request, "home_auth/change_password.html", {})

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
            context = {
                "base_url": st.BASE_URL,
                "error": "Page Not Found."
            }
            return render(request, 'home_auth/index.html', context)

    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login to access this page."
        }
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
                        'date': str(feedback_obj.timestamp.strftime("%d %B, %Y, %H:%M:%S"))
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
                        'date': str(feedback_obj.timestamp.strftime("%d %B, %Y, %H:%M:%S"))
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
    if request.user.is_authenticated:
        std_obj = Students.objects.get(auth_id=request.session["User"])
        print(std_obj)
        committeeqs = Committee_Details.objects.all()
        complaints_of_students_qs = Complaints_of_Students.objects.filter(student_id=std_obj)
        context = {
            "base_url": st.BASE_URL,
            "committees": committeeqs,
            "complaints_of_students": complaints_of_students_qs,
            "name": str(std_obj.first_name) + " " + str(std_obj.last_name)
        }

        if request.method == 'POST':
            try:
                std_obj = Students.objects.get(auth_id=request.user)

                com_id = request.POST.get('committee')
                com_obj = Committee_Details.objects.get(id=com_id)

                complaint_details = request.POST.get('complaint')

                complaints_of_student_obj = Complaints_of_Students.objects.create(
                    student_id=std_obj,
                    committee_id=com_obj,
                    complaint_details=complaint_details
                )
                complaints_of_student_obj.save()
                context["success"] = "Complaint registered successfully."
                return render(request, "students/student_complaint_section.html", context)
            except:
                context["error"] = "Some technical problem occured."
                return render(request, "students/student_complaint_section.html", context)
        else:
            return render(request, "students/student_complaint_section.html", context)
    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login to access this page."
        }
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
    if request.user.is_authenticated:
        user_obj = User.objects.get(id=request.session["User"])
        print(user_obj)
        fac_obj = Faculty.objects.get(auth_id=user_obj)
        print(fac_obj)
        if fac_obj.hod:
            return HttpResponseRedirect('/hod/dashboard/')
        committeeqs = Committee_to_Members_Mapping.objects.filter(faculty_id=fac_obj)
        departments = Departments.objects.all()

        try:
            news_qs = News.objects.order_by('-timestamp')[10]
        except IndexError as e:
            print(e)
            news_qs = News.objects.order_by('-timestamp')
            print(news_qs)

        context = {
            "base_url": st.BASE_URL,
        }

        print(news_qs)
        context["news"] = news_qs
        context["name"] = str(fac_obj.name)
        context["dept"] = fac_obj.dept_id
        context["committees"] = committeeqs
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


def FacultyComplaintSectionView(request):
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.session["User"])
        print(fac_obj)
        committeeqs = Committee_Details.objects.all()
        complaints_of_faculties_qs = Complaints_of_Facultys.objects.filter(faculty_id=fac_obj)
        context = {
            "base_url": st.BASE_URL,
            "committees": committeeqs,
            "complaints_of_faculties": complaints_of_faculties_qs

        }
        context["name"] = str(fac_obj.name)

        if request.method == 'POST':
            try:
                fac_obj = Faculty.objects.get(auth_id=request.user)

                com_id = request.POST.get('committee')
                com_obj = Committee_Details.objects.get(id=com_id)

                complaint_details = request.POST.get('complaint')

                complaints_of_faculty_obj = Complaints_of_Facultys.objects.create(
                    faculty_id=fac_obj,
                    committee_id=com_obj,
                    complaint_details=complaint_details
                )
                complaints_of_faculty_obj.save()
                context["success"] = "Complaint registered successfully."
                return render(request, "faculty/faculty_complaint_section.html", context)
            except:
                context["error"] = "Some technical problem occured."
                return render(request, "faculty/faculty_complaint_section.html", context)
        else:
            return render(request, "faculty/faculty_complaint_section.html", context)
    else:
        context = {
            "base_url": st.BASE_URL
        }
        context["error"] = "Login to access this page."
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
        context["faculty"] = fac_obj
        # context["name"] = fac_obj.name
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
        return render(request, 'hod/hod_manage_department.html', context)
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
                if request.GET.get('info') is not None:
                    data = eval(request.GET.get('info'))
                    print(data)
                    if data['type'] == 'update':
                        try:
                            subject_obj = Subjects.objects.get(id=int(data['subject_id']), dept_id=fac_obj.dept_id)
                            subject_obj.subject_name = str(data['subject_name'])
                            subject_obj.subject_code = str(data['subject_code'])
                            subject_obj.semester = int(data['subject_semester'])
                            subject_obj.save()
                            Subject_to_Faculty_Mapping.objects.filter(subject_id=subject_obj).delete()
                            for i in data['teaching_faculty']:
                                faculty_obj = Faculty.objects.get(id=int(data['teaching_faculty'][i]['id']))
                                mapping_obj = Subject_to_Faculty_Mapping.objects.create(
                                    subject_id=subject_obj,
                                    faculty_id=faculty_obj
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

                    elif data['type'] == 'delete':
                        try:
                            subject_obj = Subjects.objects.get(id=int(data['subject_id']))
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

                    elif data['type'] == 'add':
                        try:
                            subject_obj = Subjects.objects.create(
                                subject_name=str(data['subject_name']),
                                subject_code=str(data['subject_code']),
                                dept_id=fac_obj.dept_id,
                                semester=int(data['subject_semester'])
                            )
                            subject_obj.save()
                            for i in data['teaching_faculty']:
                                print(i)
                                faculty_obj = Faculty.objects.get(id=int(i))
                                mapping_obj = Subject_to_Faculty_Mapping.objects.create(
                                    subject_id=subject_obj,
                                    faculty_id=faculty_obj
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
                        "date": str(feedback_qs.latest().timestamp.strftime("%d %B, %Y, %H:%M:%S"))
                    }

                except Mid_Sem_Feedback_Answers.DoesNotExist:
                    data = {
                        "ratings": rating_list,
                        "date": str(datetime.datetime.now().strftime("%d %B, %Y, %H:%M:%S"))
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
                        "date": str(feedback_qs.latest().timestamp.strftime("%d %B, %Y, %H:%M:%S"))
                    }

                except End_Sem_Feedback_Answers.DoesNotExist:
                    data = {
                        "ratings": rating_list,
                        "date": str(datetime.datetime.now().strftime("%d %B, %Y, %H:%M:%S"))
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
                        'date': str(i.timestamp.strftime("%d %B, %Y, %H:%M:%S")),
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
                        'date': str(i.timestamp.strftime("%d %B, %Y, %H:%M:%S")),
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
        committee_qs = Committee_Details.objects.all()
        principal_obj = Principal.objects.get(auth_id=request.user)
        dept_qs = Departments.objects.all()
        context["departments"] = dept_qs
        context["name"] = principal_obj.name
        context["committees"] = committee_qs
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
                        commitee_name = request.GET.get('committee_name')
                        committee_details = request.GET.get('committee_details')
                        chairperson_id = request.GET.get('chairperson_id')
                        committee_obj = Committee_Details.objects.get(id=int(committee_id))
                        print(committee_obj)
                        committee_obj.committee_name = commitee_name
                        committee_obj.committee_details = committee_details
                        committee_obj.chairperson = Faculty.objects.get(id=int(chairperson_id))
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
                        committee_obj = Committee_Details.objects.get(id=int(committee_id))
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
            print(type)
            fb_type = ''
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
            print(type)
            fb_type = ''
            if (type == "0"):
                fb_type = "mid"
            else:
                fb_type = "end"
            return DownloadAverageFeedback(request, type=fb_type)
    else:
        return render(request, 'principal/detailed_feedback.html', context)


# Principal Related Views > End

# Committee Related Views > Start
def CommitteeDashboard(request, com_id):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        user_obj = User.objects.get(id=request.session["User"])
        fac_obj = Faculty.objects.get(auth_id=user_obj)
        com_obj = Committee_Details.objects.get(id=com_id)

        pendingstudentcomplaintsqs = Complaints_of_Students.objects.filter(committee_id=com_obj, status=1)
        pendingfacultycomplaintsqs = Complaints_of_Facultys.objects.filter(committee_id=com_obj, status=1)
        result_list = list(chain(pendingstudentcomplaintsqs, pendingfacultycomplaintsqs))

        closedstudentcomplaintsqs = Complaints_of_Students.objects.filter(committee_id=com_obj, status=0)
        closedfacultycomplaintsqs = Complaints_of_Facultys.objects.filter(committee_id=com_obj, status=0)
        result_list2 = list(chain(closedstudentcomplaintsqs, closedfacultycomplaintsqs))

        # print(result_list)
        context['pending_complaints'] = result_list
        context['closed_complaints'] = result_list2
        context["com_obj"] = com_obj
        context["name"] = str(fac_obj.name)
        context["dept"] = fac_obj.dept_id

        return render(request, 'committees/committee_dashboard.html', context)
    else:
        context = {
            "base_url": st.BASE_URL,
        }
        context["error"] = "Login First."
        return render(request, "home_auth/index.html", context)


# Committee Related Views > End

# Download Report Views > Start
def DownloadDetailedFeedback(request, type):
    if type == "mid":
        if request.user.is_authenticated:
            if request.method == "POST":
                if request.POST.get('faculty') is not None:
                    faculty_id = request.POST.get('faculty')
                    term = request.POST.get('term')
                    year = request.POST.get('year')
                    print(faculty_id, term, year)
                    print(request.META['HTTP_REFERER'])

                    return HttpResponse("Detailed Feedback")

    elif type == "end":
        if request.user.is_authenticated:
            if request.method == "POST":
                if request.POST.get('faculty') is not None:
                    faculty_id = request.POST.get('faculty')
                    term = request.POST.get('term')
                    year = request.POST.get('year')
                    print(faculty_id, term, year)
                    print(request.META['HTTP_REFERER'])

                    return HttpResponse("Detailed Feedback")

    else:
        pass


def DownloadAverageFeedback(request, type):
    if type == "mid":
        if request.user.is_authenticated:
            if request.method == "POST":
                if request.POST.get('faculty') is not None:
                    faculty_id = request.POST.get('faculty')
                    term = request.POST.get('term')
                    year = request.POST.get('year')
                    is_all_subject = request.POST.get('all_subject')
                    if not is_all_subject:
                        subject_id = request.POST.get('subject')
                        print(faculty_id, term, year, is_all_subject, subject_id)
                    else:
                        print(faculty_id, term, year, is_all_subject)
                    print(request.META['HTTP_REFERER'])

                    return HttpResponse("Average Feedback")

    elif type == "end":
        if request.user.is_authenticated:
            if request.method == "POST":
                if request.POST.get('faculty') is not None:
                    faculty_id = request.POST.get('faculty')
                    term = request.POST.get('term')
                    year = request.POST.get('year')
                    is_all_subject = request.POST.get('all_subject')
                    if not is_all_subject:
                        subject_id = request.POST.get('subject')
                        print(faculty_id, term, year, is_all_subject, subject_id)
                    else:
                        print(faculty_id, term, year, is_all_subject)
                    print(request.META['HTTP_REFERER'])

                    return HttpResponse("Average Feedback")

    else:
        pass


# Download Report Views > End

def Misc(request):
    return render(request, 'home_auth/forgot_password.html', {})
