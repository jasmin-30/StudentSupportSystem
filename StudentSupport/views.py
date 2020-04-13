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
                student_obj = Students.objects.get(auth_id=user_obj)
            except Exception as e:
                print(e)
                context["error"] = "You are not a registered User."
                return render(request, "home_auth/index.html", context)

            email_to = email_forgot
            email_from = st.EMAIL_HOST_USER
            email_encrypted = b64encode(email_to.encode())
            url = st.BASE_URL + "changePassword/?email=" + email_encrypted.decode('utf-8')
            # print(email_to, email_from)
            subject = "Recover Your Password."
            html_message = render_to_string('email_templates/recover_password_template.html',
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

    if request.user.is_authenticated:
        student_obj = Students.objects.get(auth_id=request.user)
        departments = Departments.objects.all()

        context = {
            "base_url": st.BASE_URL,
            "std_obj": student_obj,
            "departments": departments,
            "name": str(student_obj.first_name) + " " + str(student_obj.last_name),
            "email": request.user.email
        }
        dept_obj = Departments.objects.get(id = student_obj.dept_id.id)
        context["department"] = dept_obj.dept_name

        if request.method == "POST":
            if request.POST.get('fname') is not None:
                student_obj = Students.objects.get(auth_id=request.user)
                user_obj = User.objects.get(id = request.user.id)
                fname = request.POST.get('fname')
                lname = request.POST.get('lname')
                email = request.POST.get('email')

                student_obj.first_name = fname
                student_obj.last_name = lname
                student_obj.save()

                user_obj.email = email
                user_obj.save()
                request.user = user_obj

                context = {
                    "base_url": st.BASE_URL,
                    "std_obj": student_obj,
                    "success": "Profile Updated Successfully",
                    "name": str(student_obj.first_name) + " " + str(student_obj.last_name),
                    "email": request.user.email
                }

                dept_obj = Departments.objects.get(id=student_obj.dept_id.id)
                context["department"] = dept_obj.dept_name
                return render(request, 'students/student_profile_page.html', context)

            elif request.POST.get('sem') is not None:
                student_obj = Students.objects.get(auth_id=request.user)
                sem = request.POST.get('sem')

                student_obj.semester = sem
                student_obj.save()

                context = {
                    "base_url": st.BASE_URL,
                    "std_obj": student_obj,
                    "success": "Profile Updated Successfully",
                    "name": str(student_obj.first_name) + " " + str(student_obj.last_name),
                    "email": request.user.email
                }

                dept_obj = Departments.objects.get(id=student_obj.dept_id.id)
                context["department"] = dept_obj.dept_name
                return render(request, 'students/student_profile_page.html', context)

            elif request.POST.get('newpwd') is not None:
                oldpwd = request.POST.get('oldpwd')
                newpwd = request.POST.get('newpwd')
                pwd = request.user.password
                if check_password(oldpwd, pwd):
                    try:
                        student_obj = Students.objects.get(auth_id=request.user)
                        user_obj = User.objects.get(id=request.user.id)
                        user_obj.set_password(str(newpwd))
                        user_obj.save()
                        update_session_auth_hash(request, user_obj)

                        context = {
                            "base_url": st.BASE_URL,
                            "std_obj": student_obj,
                            "success": "Password Changed Successfully.",
                            "name": str(student_obj.first_name) + " " + str(student_obj.last_name),
                            "email": request.user.email
                        }

                        dept_obj = Departments.objects.get(id=student_obj.dept_id.id)
                        context["department"] = dept_obj.dept_name
                        return render(request, 'students/student_profile_page.html', context)

                    except Exception as e:
                        context["error"] = "Error in changing password. please try again later."
                        context["name"] = str(student_obj.first_name) + " " + str(student_obj.last_name)
                        context["email"] = request.user.email
                        dept_obj = Departments.objects.get(id=student_obj.dept_id.id)
                        context["department"] = dept_obj.dept_name
                        return render(request, 'students/student_profile_page.html', context)
                else:
                    student_obj = Students.objects.get(auth_id=request.user)
                    context = {
                        "base_url": st.BASE_URL, "std_obj": student_obj,
                        "error": "Old Password does not match with the one you entered. Please enter correct password.",
                        "name": str(student_obj.first_name) + " " + str(student_obj.last_name),
                        "email": request.user.email
                    }

                    dept_obj = Departments.objects.get(id=student_obj.dept_id.id)
                    context["department"] = dept_obj.dept_name
                    return render(request, 'students/student_profile_page.html', context)
        else:
            return render(request, 'students/student_profile_page.html', context)

    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login to access profile page."
        }
        return render(request, 'home_auth/index.html', context)


# TODO : Optimize it.
def StudentMidSemFeedbackView(request):
    if request.user.is_authenticated:
        std_obj = Students.objects.get(auth_id=request.session["User"])
        dept_id = std_obj.dept_id

        sem1_subqs = Subjects.objects.filter(dept_id=dept_id, semester=1)
        sem2_subqs = Subjects.objects.filter(dept_id=dept_id, semester=2)
        sem3_subqs = Subjects.objects.filter(dept_id=dept_id, semester=3)
        sem4_subqs = Subjects.objects.filter(dept_id=dept_id, semester=4)
        sem5_subqs = Subjects.objects.filter(dept_id=dept_id, semester=5)
        sem6_subqs = Subjects.objects.filter(dept_id=dept_id, semester=6)
        sem7_subqs = Subjects.objects.filter(dept_id=dept_id, semester=7)
        sem8_subqs = Subjects.objects.filter(dept_id=dept_id, semester=8)
        questions = Mid_Sem_Feedback_Questions.objects.all()

        context = {
            "base_url": st.BASE_URL,
            "sem1_subqs": sem1_subqs,
            "sem2_subqs": sem2_subqs,
            "sem3_subqs": sem3_subqs,
            "sem4_subqs": sem4_subqs,
            "sem5_subqs": sem5_subqs,
            "sem6_subqs": sem6_subqs,
            "sem7_subqs": sem7_subqs,
            "sem8_subqs": sem8_subqs,
            "questions": questions,
            "name": str(std_obj.first_name) + " " + str(std_obj.last_name)
        }

        if request.method == 'POST':
            try:
                std_obj = Students.objects.get(auth_id=request.user)

                dept_obj = Departments.objects.get(id=std_obj.dept_id.id)

                sub_id = request.POST.get('subject_id')
                sub_obj = Subjects.objects.get(id=sub_id)

                fac_id = request.POST.get('faculty_id')
                fac_obj = Faculty.objects.get(id=fac_id)

                semester = std_obj.semester

                ans1 = request.POST.get('optradio_1')
                ans2 = request.POST.get('optradio_2')
                ans3 = request.POST.get('optradio_3')
                ans4 = request.POST.get('optradio_4')
                ans5 = request.POST.get('optradio_5')
                ans6 = request.POST.get('optradio_6')
                ans7 = request.POST.get('optradio_7')
                ans8 = request.POST.get('optradio_8')
                ans9 = request.POST.get('optradio_9')
                ans10 = request.POST.get('optradio_10')
                remarks = request.POST.get('remarks')

                mid_sem_feedback_ans_obj = Mid_Sem_Feedback_Answers.objects.create(
                    student_id=std_obj,
                    dept_id=dept_obj,
                    subject_id=sub_obj,
                    faculty_id=fac_obj,
                    semester=semester,
                    Q1=ans1,
                    Q2=ans2,
                    Q3=ans3,
                    Q4=ans4,
                    Q5=ans5,
                    Q6=ans6,
                    Q7=ans7,
                    Q8=ans8,
                    Q9=ans9,
                    Q10=ans10,
                    remarks=remarks
                )
                mid_sem_feedback_ans_obj.save()
                student_feedback_status_obj = Student_Feedback_Status.objects.filter(
                    student_id=std_obj,
                    subject_id=sub_obj
                ).update(is_given=True)

                context["success"] = "Thank you for giving your feedback."
                return render(request, "students/student_mid_sem_feedback.html", context)
            except:
                context["error"] = "Some technical problem occured."
                return render(request, "students/student_mid_sem_feedback.html", context)

        else:
            return render(request, "students/student_mid_sem_feedback.html", context)
    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login to access this page."
        }
        return render(request, 'home_auth/index.html', context)


def StudentEndSemFeedbackView(request):
    if request.user.is_authenticated:
        std_obj = Students.objects.get(auth_id = request.session["User"])
        dept_id = std_obj.dept_id

        sem1_subqs = Subjects.objects.filter(dept_id = dept_id, semester=1)
        sem2_subqs = Subjects.objects.filter(dept_id = dept_id, semester=2)
        sem3_subqs = Subjects.objects.filter(dept_id = dept_id, semester=3)
        sem4_subqs = Subjects.objects.filter(dept_id = dept_id, semester=4)
        sem5_subqs = Subjects.objects.filter(dept_id = dept_id, semester=5)
        sem6_subqs = Subjects.objects.filter(dept_id = dept_id, semester=6)
        sem7_subqs = Subjects.objects.filter(dept_id = dept_id, semester=7)
        sem8_subqs = Subjects.objects.filter(dept_id = dept_id, semester=8)
        questions = End_Sem_Feedback_Questions.objects.all()
        context = {
            "base_url": st.BASE_URL,
            "sem1_subqs": sem1_subqs,
            "sem2_subqs": sem2_subqs,
            "sem3_subqs": sem3_subqs,
            "sem4_subqs": sem4_subqs,
            "sem5_subqs": sem5_subqs,
            "sem6_subqs": sem6_subqs,
            "sem7_subqs": sem7_subqs,
            "sem8_subqs": sem8_subqs,
            "questions": questions,
            "name": str(std_obj.first_name) + " " + str(std_obj.last_name)
        }

        if request.method == 'POST':
            std_obj = Students.objects.get(auth_id=request.user)

            dept_obj = Departments.objects.get(id=std_obj.dept_id.id)

            sub_id = request.POST.get('subject_id')
            sub_obj = Subjects.objects.get(id=sub_id)

            fac_id = request.POST.get('faculty_id')
            fac_obj = Faculty.objects.get(id=fac_id)

            semester = std_obj.semester

            ans1 = request.POST.get('optradio_1')
            ans2 = request.POST.get('optradio_2')
            ans3 = request.POST.get('optradio_3')
            ans4 = request.POST.get('optradio_4')
            ans5 = request.POST.get('optradio_5')
            ans6 = request.POST.get('optradio_6')
            ans7 = request.POST.get('optradio_7')
            ans8 = request.POST.get('optradio_8')
            ans9 = request.POST.get('optradio_9')
            ans10 = request.POST.get('optradio_10')
            remarks = request.POST.get('remarks')
            # print(std_id, dept_id, sub_id, fac_id, semester, ans1, ans2, ans3, ans4, ans5, ans6, ans7, ans8, ans9, ans10, remarks)

            try:
                end_sem_feedback_ans_obj = End_Sem_Feedback_Answers.objects.create(
                    student_id = std_obj,
                    dept_id = dept_obj,
                    subject_id = sub_obj,
                    faculty_id = fac_obj,
                    semester = semester,
                    Q1 = ans1,
                    Q2 = ans2,
                    Q3 = ans3,
                    Q4 = ans4,
                    Q5 = ans5,
                    Q6 = ans6,
                    Q7 = ans7,
                    Q8 = ans8,
                    Q9 = ans9,
                    Q10 = ans10,
                    remarks = remarks
                )
                end_sem_feedback_ans_obj.save()

                student_feedback_status_obj = Student_Feedback_Status.objects.filter(
                    student_id=std_obj,
                    subject_id=sub_obj
                ).update(end_sem_is_given=True)

                context["success"] = "Thank you for giving your feedback"
                return render(request, "students/student_end_sem_feedback.html", context)
            except:
                context["error"] = "Some technical problem occured."
                return render(request, "students/student_end_sem_feedback.html", context)
        else:
            return render(request, "students/student_end_sem_feedback.html", context)
    else:
        context = {
            "base_url": st.BASE_URL,
            "error": "Login to access this page."
        }
        return render(request, 'home_auth/index.html', context)


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
                com_obj = Committee_Details.objects.get(id = com_id)

                complaint_details = request.POST.get('complaint')

                complaints_of_student_obj = Complaints_of_Students.objects.create(
                    student_id = std_obj,
                    committee_id = com_obj,
                    complaint_details = complaint_details
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


def getFacultyName(request):
    sub_id = request.GET['sub_id_gf']
    obj = Subject_to_Faculty_Mapping.objects.get(subject_id=int(sub_id))
    faculty = Faculty.objects.get(id=obj.faculty_id.id)
    faculty_id = faculty.id
    faculty_name = faculty.name
    result = json.dumps({'name': faculty_name, 'id': faculty_id})
    return HttpResponse(result)


def checkStatus(request):
    std_obj = Students.objects.get(auth_id=request.user)
    sub_id = request.GET['sub_id']
    sub_obj = Subjects.objects.get(id=int(sub_id))
    # print("Hello")
    # print(sub_id, sub_obj)
    feedback_given_obj = Student_Feedback_Status.objects.get(student_id=std_obj, subject_id=sub_obj)
    print(feedback_given_obj.is_given)
    if (feedback_given_obj.is_given == True):
        result = json.dumps({'v': '1'})
    else:
        result = json.dumps({'v': '0'})
    return HttpResponse(result)


def checkStatusforEndSem(request):
    std_obj = Students.objects.get(auth_id=request.user)
    sub_id = request.GET['sub_id']
    sub_obj = Subjects.objects.get(id=int(sub_id))
    # print("Hello")
    # print(sub_id, sub_obj)
    feedback_given_obj = Student_Feedback_Status.objects.get(student_id=std_obj, subject_id=sub_obj)
    print(feedback_given_obj.end_sem_is_given)
    if (feedback_given_obj.end_sem_is_given == True):
        result = json.dumps({'v': '1'})
    else:
        result = json.dumps({'v': '0'})
    return HttpResponse(result)


def GetFeedback(request):
    std_obj = Students.objects.get(auth_id=request.user)
    sub_id = request.GET['subject_id']
    sub_obj = Subjects.objects.get(id=int(sub_id))

    mid_sem_feedback_answer_obj = Mid_Sem_Feedback_Answers.objects.get(student_id=std_obj, subject_id=sub_obj)

    result = json.dumps({'a1': mid_sem_feedback_answer_obj.Q1,
                         'a2': mid_sem_feedback_answer_obj.Q2,
                         'a3': mid_sem_feedback_answer_obj.Q3,
                         'a4': mid_sem_feedback_answer_obj.Q4,
                         'a5': mid_sem_feedback_answer_obj.Q5,
                         'a6': mid_sem_feedback_answer_obj.Q6,
                         'a7': mid_sem_feedback_answer_obj.Q7,
                         'a8': mid_sem_feedback_answer_obj.Q8,
                         'a9': mid_sem_feedback_answer_obj.Q9,
                         'a10': mid_sem_feedback_answer_obj.Q10,
                         'remarks': mid_sem_feedback_answer_obj.remarks
                         })
    return HttpResponse(result)


def GetFeedbackForEndSem(request):
    std_obj = Students.objects.get(auth_id=request.user)
    sub_id = request.GET['subject_id']
    sub_obj = Subjects.objects.get(id=int(sub_id))

    end_sem_feedback_answer_obj = End_Sem_Feedback_Answers.objects.get(student_id=std_obj, subject_id=sub_obj)

    result = json.dumps({'a1': end_sem_feedback_answer_obj.Q1,
                         'a2': end_sem_feedback_answer_obj.Q2,
                         'a3': end_sem_feedback_answer_obj.Q3,
                         'a4': end_sem_feedback_answer_obj.Q4,
                         'a5': end_sem_feedback_answer_obj.Q5,
                         'a6': end_sem_feedback_answer_obj.Q6,
                         'a7': end_sem_feedback_answer_obj.Q7,
                         'a8': end_sem_feedback_answer_obj.Q8,
                         'a9': end_sem_feedback_answer_obj.Q9,
                         'a10': end_sem_feedback_answer_obj.Q10,
                         'remarks': end_sem_feedback_answer_obj.remarks
                         })
    return HttpResponse(result)


# Student Related Views > End


# Faculty Related Views > Start
def FacultyDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        if (fac_obj.hod):
            return HttpResponseRedirect('/hod/dashboard')
        context["name"] = fac_obj.name
        try:
            news_qs = News.objects.order_by('-timestamp')[10]
        except IndexError as e:
            print(e)
            news_qs = News.objects.order_by('-timestamp')
            print(news_qs)

        print(news_qs)
        context["news"] = news_qs
        if not fac_obj.active:
            context[
                "pnotify"] = "You have been removed from " + fac_obj.dept_id.dept_name + " Department. But you can still access feedback."

        return render(request, 'faculty/dashboard_faculty.html', context)
    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'faculty/dashboard_faculty.html', context)


def FacultyViewDetailedFeedback(request, type):
    print(type)
    return render(request, 'faculty/view_detailed_feedback.html', context={})


def FacultyViewAverageFeedback(request, type):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        subject_to_faculty_mapping_qs = Subject_to_Faculty_Mapping.objects.filter(faculty_id=fac_obj)
        print(subject_to_faculty_mapping_qs)
        context["subjects"] = subject_to_faculty_mapping_qs
        if type == "mid-sem":
            context["type"] = "Mid Semester"
            return render(request, 'faculty/view_average_feedback.html', context)
        elif type == "end-sem":
            context["type"] = "End Semester"
            return render(request, 'faculty/view_average_feedback.html', context)

    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'faculty/view_average_feedback.html', context)


def FacultyProfile(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Faculty":
        fac_obj = Faculty.objects.get(auth_id=request.user)
        context["name"] = fac_obj.name
        context["email"] = request.user.email
        context["dept"] = fac_obj.dept_id.dept_name
        dept_qs = Departments.objects.all()
        context["departments"] = dept_qs
        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                email = request.POST.get('email')
                dept = request.POST.get('dept')
                if name != fac_obj.name or email != request.user.email or dept != fac_obj.dept_id.id:
                    fac_obj.name = name
                    fac_obj.dept_id = Departments.objects.get(id=int(dept))
                    fac_obj.save()
                    user_obj = User.objects.get(id=request.user.id)
                    user_obj.email = email
                    user_obj.save()
                    request.user = user_obj
                    context["success"] = "Profile Updated Successfully"
                    context["name"] = fac_obj.name
                    context["email"] = request.user.email
                    context["dept"] = fac_obj.dept_id.dept_name
                    return render(request, 'faculty/faculty_profile_page.html', context)

                else:
                    return render(request, 'faculty/faculty_profile_page.html', context)

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
                        return render(request, 'faculty/faculty_profile_page.html', context)
                    except Exception as e:
                        print(e)
                        context["error"] = "Error in changing password. please try again later."
                        return render(request, 'faculty/faculty_profile_page.html', context)
                else:
                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'faculty/faculty_profile_page.html', context)
        else:
            return render(request, 'faculty/faculty_profile_page.html', context)
    else:
        context["error"] = "Login first."
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
        dept_qs = Departments.objects.all()
        context["departments"] = dept_qs
        if request.method == "POST":
            if request.POST.get('name') is not None:
                name = request.POST.get('name')
                email = request.POST.get('email')
                dept = request.POST.get('dept')
                if name != fac_obj.name or email != request.user.email or dept != fac_obj.dept_id.id:
                    fac_obj.name = name
                    fac_obj.dept_id = Departments.objects.get(id=int(dept))
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
                    print(context)
                    print(res)
                    print(type(res))
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


def HodViewDetailedFeedback(request):
    return render(request, 'hod/hod_view_detailed_feedback.html', context={})


def HodViewAverageFeedback(request):
    return render(request, 'hod/hod_view_average_feedback.html', context={})


# HOD Related Views > End

# Principal Related Views > Start
def PrincipalDashboard(request):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated:
        committee_qs = Committee_Details.objects.all()
        user_obj = User.objects.get(id=request.session["User"])
        principal_obj = Principal.objects.get(auth_id=user_obj)
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
        context["error"] = "Login first to access dashboard."
        return render(request, 'home_auth/index.html', context)


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
    else:
        context["error"] = "You are not authorized to view this page."
        return render(request, 'home_auth/index.html', context)


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
                    context[
                        "error"] = "Old Password does not match with the one you entered. Please enter correct password."
                    return render(request, 'principal/principal_profile_page.html', context)
        else:
            return render(request, 'principal/principal_profile_page.html', context)

    else:
        context["error"] = "Login to access dashboard."
        return render(request, 'home_auth/index.html', context)


# Principal Related Views > End

def DepartmentsView(request, dept):
    context = {
        "base_url": st.BASE_URL,
    }
    if request.user.is_authenticated and request.user.getRole == "Principal":
        principal_obj = Principal.objects.get(auth_id=request.user)
        context["name"] = principal_obj.name
        fac_qs = Faculty.objects.filter(dept_id__accronym__exact=dept)
        dept_name = Departments.objects.get(accronym__exact=dept).dept_name
        context["faculties"] = fac_qs
        context["dept_name"] = dept_name
        return render(request, 'principal/department.html', context)
    else:
        context["error"] = "You are not authorized to view this page."


# Committee Related Views > Start
def CommitteeDashboard(request, committee):
    print(committee)
    return render(request, 'committees/committee_dashboard.html', context={})

# Committee Related Views > End
