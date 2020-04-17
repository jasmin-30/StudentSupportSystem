# TODO : News model need to be changed. News should be department specific.
# TODO : Remove Course Exit Survey Tables.
# TODO : optimize all models.
# TODO : Take care of models.CASCADE field in every foriegn keys.
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin, AbstractUser)
from django.db import models
from django.conf import settings


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_staff=False, is_active=False, is_admin=False, role="Student"):
        if not email:
            raise ValueError("User must have an email address")

        if not password:
            raise ValueError("User must have an password")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.set_password(password)
        user.staff = is_staff
        user.admin = is_admin
        user.role = role
        # user.is_superuser = is_superuser
        user.active = is_active
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(email, password=password, is_staff=True, is_admin=True, is_active=True)
        user.is_superuser = True
        user.save(using=self._db)
        # user.is_superuser = True
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Database model for users in thr system"""
    ROLE = (
        ("Student", "Student"),
        ("Faculty", "Faculty"),
        ("Principal", "Principal")
    )
    email = models.EmailField(max_length=255, unique=True)
    role = models.CharField(choices=ROLE, default="Student", max_length=20, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    # confirm = models.BooleanField(default=False)
    # confirmed_date = models.DateTimeField(default=datetime.datetime.now())
    password = models.CharField(max_length=255)
    active = models.BooleanField(default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    def get_full_name(self):
        """Retrieve full name of user"""
        return self.email

    def get_short_name(self):
        """Retrieve short name of the user"""
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        return self.staff

    @property
    def getRole(self):
        return self.role

    @property
    def is_active(self):
        return self.active

    @property
    def is_admin(self):
        return self.admin


#
# # Create your models here.
#
# # Overloading the default user manager
# # class UserManager(BaseUserManager):
# #     def create_user(self, email, password="12345", staff=False, admin=False, active=True):
# #         if not email:
# #             raise ValueError("User must have an email address")
# #
# #         user_obj = self.model(
# #             email=self.normalize_email(email)
# #         )
# #         user_obj.set_password(password)
# #         user_obj.staff = staff
# #         user_obj.active = active
# #
# #         user_obj.save(using=self._db)
# #         return user_obj
# #
#
#
# # Custom user model
# class User(AbstractBaseUser):
#     ROLE = (
#         ("Student", "Student"),
#         ("Faculty", "Faculty"),
#         ("Principal", "Principal")
#     )
#     email = models.EmailField(max_length=255, unique=True)
#     # full_name = models.CharField(max_length=255)
#     active = models.BooleanField(default=True)  # Login in general
#     staff = models.BooleanField(default=False)  # Staff user non superuser
#     admin = models.BooleanField(default=False)  # Superuser
#     role = models.CharField(choices=ROLE, default="Student", max_length=20)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     confirm = models.BooleanField(default=False)
#     confirmed_date = models.DateTimeField(default=False)
#
#     # objects = UserManager()
#
#     # Definined USername Field
#     USERNAME_FIELD = email
#
#     # Required Field
#     REQUIRED_FIELDS = []
#
#     def __str__(self):
#         return self.email
#
#     def get_full_name(self):
#         return self.email
#
#     def get_short_name(self):
#         return self.email
#
#     def is_confirmed(self):
#         return self.confirm
#
#     @property
#     def is_staff(self):
#         return self.staff
#
#     @property
#     def is_active(self):
#         return self.active
#
#     @property
#     def is_admin(self):
#         return self.admin
#
#
# Models to store information about all the departments.
class Principal(models.Model):
    name = models.CharField(max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.auth_id)


class Departments(models.Model):
    dept_name = models.CharField(max_length=100)
    accronym = models.CharField(max_length=10, default=None)

    def __str__(self):
        return self.dept_name


class Faculty(models.Model):
    name = models.CharField(max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default=None)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, null=True)
    hod = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def is_hod(self):
        return self.hod

    def __str__(self):
        return str(self.name) + " : " + str(self.auth_id)


class Students(models.Model):
    SEMESTER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
    )
    enrollment_no = models.CharField(max_length=12, primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default=None)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.SET_NULL, null=True)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.enrollment_no


class Subjects(models.Model):
    SEMESTER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
    )
    subject_name = models.CharField(max_length=255)
    subject_code = models.CharField(max_length=10)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.subject_name) + " : " + str(self.dept_id.dept_name) + " : " + str(self.semester)


class Subject_to_Faculty_Mapping(models.Model):
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.faculty_id) + "->" + str(self.subject_id)


class End_Sem_Feedback_Questions(models.Model):
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class End_Sem_Feedback_Answers(models.Model):
    SEMESTER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
    )
    RATINGS = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    Q1 = models.IntegerField(choices=RATINGS, default=0)
    Q2 = models.IntegerField(choices=RATINGS, default=0)
    Q3 = models.IntegerField(choices=RATINGS, default=0)
    Q4 = models.IntegerField(choices=RATINGS, default=0)
    Q5 = models.IntegerField(choices=RATINGS, default=0)
    Q6 = models.IntegerField(choices=RATINGS, default=0)
    Q7 = models.IntegerField(choices=RATINGS, default=0)
    Q8 = models.IntegerField(choices=RATINGS, default=0)
    Q9 = models.IntegerField(choices=RATINGS, default=0)
    Q10 = models.IntegerField(choices=RATINGS, default=0)
    remarks = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id)


class Mid_Sem_Feedback_Questions(models.Model):
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class Mid_Sem_Feedback_Answers(models.Model):
    SEMESTER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8)
    )
    RATINGS = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    Q1 = models.IntegerField(choices=RATINGS, default=0)
    Q2 = models.IntegerField(choices=RATINGS, default=0)
    Q3 = models.IntegerField(choices=RATINGS, default=0)
    Q4 = models.IntegerField(choices=RATINGS, default=0)
    Q5 = models.IntegerField(choices=RATINGS, default=0)
    Q6 = models.IntegerField(choices=RATINGS, default=0)
    Q7 = models.IntegerField(choices=RATINGS, default=0)
    Q8 = models.IntegerField(choices=RATINGS, default=0)
    Q9 = models.IntegerField(choices=RATINGS, default=0)
    Q10 = models.IntegerField(choices=RATINGS, default=0)
    remarks = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id) + " : " + str(self.faculty_id.name) + " : " + str(self.subject_id.subject_name)


# class Course_Exit_Survey_Questions(models.Model):
#     SEMESTER = (
#         (1, 1),
#         (2, 2),
#         (3, 3),
#         (4, 4),
#         (5, 5),
#         (6, 6),
#         (7, 7),
#         (8, 8)
#     )
#     dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
#     subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
#     faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
#     question_text = models.TextField()
#     semester = models.IntegerField(choices=SEMESTER, default=1)
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return str(self.faculty_id)
#
#
# class Course_Exit_Survey_Answers(models.Model):
#     SEMESTER = (
#         (1, 1),
#         (2, 2),
#         (3, 3),
#         (4, 4),
#         (5, 5),
#         (6, 6),
#         (7, 7),
#         (8, 8)
#     )
#     RATINGS = (
#         (1, 1),
#         (2, 2),
#         (3, 3),
#         (4, 4),
#         (5, 5)
#     )
#     student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
#     dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
#     subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
#     survey_id = models.ForeignKey(Course_Exit_Survey_Questions, to_field='id', on_delete=models.CASCADE)
#     semester = models.IntegerField(choices=SEMESTER, default=1)
#     Q1 = models.IntegerField(choices=RATINGS, default=1)
#     Q2 = models.IntegerField(choices=RATINGS, default=1)
#     Q3 = models.IntegerField(choices=RATINGS, default=1)
#     Q4 = models.IntegerField(choices=RATINGS, default=1)
#     Q5 = models.IntegerField(choices=RATINGS, default=1)
#     remarks = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return str(self.student_id) + str(self.survey_id)


class Program_Exit_Survey_Questions(models.Model):
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class Program_Exit_Survey_Answers(models.Model):
    RATINGS = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    Q1 = models.IntegerField(choices=RATINGS, default=0)
    Q2 = models.IntegerField(choices=RATINGS, default=0)
    Q3 = models.IntegerField(choices=RATINGS, default=0)
    Q4 = models.IntegerField(choices=RATINGS, default=0)
    Q5 = models.IntegerField(choices=RATINGS, default=0)
    Q6 = models.IntegerField(choices=RATINGS, default=0)
    Q7 = models.IntegerField(choices=RATINGS, default=0)
    Q8 = models.IntegerField(choices=RATINGS, default=0)
    Q9 = models.IntegerField(choices=RATINGS, default=0)
    Q10 = models.IntegerField(choices=RATINGS, default=0)
    remarks = models.TextField(null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id)


class Committee_Details(models.Model):
    committee_name = models.CharField(max_length=100)
    committee_details = models.TextField()
    chairperson = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.committee_name


class Committee_to_Members_Mapping(models.Model):
    committee_id = models.ForeignKey(Committee_Details, to_field='id', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.committee_id) + "->" + str(self.faculty_id)


class Complaints_of_Students(models.Model):
    STATUS = (
        (0, "Closed"),
        (1, "Active/Pending"),
        (2, "Re-Opened")
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    committee_id = models.ForeignKey(Committee_Details, to_field='id', on_delete=models.CASCADE)
    complaint_details = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default=1)
    reacting_faculty = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, null=True,
                                         blank=True)
    action_taken = models.TextField(null=True, blank=True)
    report = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.complaint_details)


class Complaints_of_Facultys(models.Model):
    STATUS = (
        (0, "Closed"),
        (1, "Active/Pending"),
        (2, "Re-Opened")
    )
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    committee_id = models.ForeignKey(Committee_Details, to_field='id', on_delete=models.CASCADE)
    complaint_details = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS, default=1)
    reacting_faculty = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE)
    action_taken = models.TextField()
    report = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.complaint_details)


class News(models.Model):
    SEMESTER = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9)  # 9 means all departments
    )
    news_subject = models.TextField()
    news_details = models.TextField()
    issuing_faculty = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    target_audience = models.IntegerField(choices=SEMESTER, default=9)
    # start_date = models.DateField(auto_now_add=True)
    # expiry_date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.news_details


class Student_Feedback_Status(models.Model):
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    # is_given = models.BooleanField(default=False)
    # end_sem_is_given = models.BooleanField(default=False)
    mid_sem_feedback = models.ForeignKey(Mid_Sem_Feedback_Answers, to_field='id', on_delete=models.CASCADE, null=True)
    end_sem_feedback = models.ForeignKey(End_Sem_Feedback_Answers, to_field='id', on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id) + " : " + str(self.subject_id.subject_name) + " : " + str(self.faculty_id.name)
