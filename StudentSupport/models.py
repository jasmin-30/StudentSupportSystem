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
    email = models.EmailField('Email ID', max_length=255, unique=True)
    role = models.CharField('Role', choices=ROLE, default="Student", max_length=20)
    timestamp = models.DateTimeField('Registered Date', auto_now_add=True)
    # confirm = models.BooleanField(default=False)
    # confirmed_date = models.DateTimeField(default=datetime.datetime.now())
    password = models.CharField(max_length=255)
    active = models.BooleanField('Confirmed or Not', default=False)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField('Superuser', default=False)
    requested_change_password = models.BooleanField(default=False)

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


# Model to store information of principal
class Principal(models.Model):
    name = models.CharField('Name', max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE,
                                verbose_name=u'User Email')

    def __str__(self):
        return str(self.auth_id)


# Model to store information of department
class Departments(models.Model):
    dept_name = models.CharField('Department Name', max_length=100)
    accronym = models.CharField('Accronym', max_length=10, default=None)
    is_mid_sem_live = models.BooleanField('Mid Semester Feedback', default=True)
    is_end_sem_live = models.BooleanField('End Semester Feedback', default=True)

    class Meta:
        verbose_name = "Departments"
        verbose_name_plural = "Departments"

    def __str__(self):
        return self.dept_name


# Model to store information of all the faculty.
class Faculty(models.Model):
    name = models.CharField('Faculty Name', max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE,
                                verbose_name=u'User Email')
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, verbose_name=u'Department')
    hod = models.BooleanField('HOD/Faculty', default=False)  # if faculty is head of department
    active = models.BooleanField('Active/Retired', default=True)  # whether faculty has been removed from department
    timestamp = models.DateTimeField('Registered Date', auto_now_add=True)

    class Meta:
        verbose_name = "Faculty"
        verbose_name_plural = "Faculties"

    @property
    def is_hod(self):
        return self.hod

    @property
    def name_email(self):
        return f'{self.name} ({self.auth_id.email})'

    def __str__(self):
        if self.hod:
            return str(self.name) + " (" + str(self.dept_id.accronym) + " HOD)"

        else:
            return str(self.name) + " (" + str(self.dept_id.accronym) + " Faculty)"


# Model to store information about students
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
    DIVISION = (
        (1, 1),
        (2, 2),
        (3, 3)
    )
    enrollment_no = models.CharField('Enrollment No', max_length=12, primary_key=True)
    first_name = models.CharField('First Name', max_length=255)
    last_name = models.CharField('Last Name', max_length=255)
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE,
                                verbose_name=u'User Email')
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, verbose_name=u'Department')
    div = models.IntegerField('Division', choices=DIVISION, default=1)  # which division student is assigned.
    semester = models.IntegerField('Semester', choices=SEMESTER, default=1)
    timestamp = models.DateTimeField('Registered Date', auto_now_add=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def Name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return str(self.enrollment_no)


# Model to store information about subjects.
# two division have same subject then two different object will be stored.
# two department have same subject then two different object will be stored.
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
    DIVISION = (
        (1, 1),
        (2, 2),
        (3, 3)
    )
    subject_name = models.CharField('Subject Name', max_length=255)
    subject_code = models.CharField('Subject Code', max_length=10)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, verbose_name=u'Department')
    div = models.IntegerField('Division', choices=DIVISION, default=1)
    semester = models.IntegerField('Semester', choices=SEMESTER, default=1)
    is_active = models.BooleanField('Removed or Not', default=True)
    timestamp = models.DateTimeField('Added Date', auto_now_add=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"

    @property
    def Name_Code(self):
        return f'{self.subject_name} ({self.subject_code})'

    def __str__(self):
        return str(self.subject_name) + " ( " + str(self.subject_code) + ") -> " + str(
            self.dept_id.dept_name) + " -> Div : " + str(
            self.div) + " -> Semester : " + str(self.semester)


# Model to store which subject is taken by which faculty.
class Subject_to_Faculty_Mapping(models.Model):
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name=u'Teaching Faculty')
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE, verbose_name=u'Subject')

    class Meta:
        verbose_name = "Subject to Faculty Mapping"
        verbose_name_plural = "Subject to Faculty Mapping"

    @property
    def Subject_Name(self):
        return f'{self.subject_id.subject_name} ({self.subject_id.subject_code})'

    @property
    def Faculty_Name(self):
        return f'{self.faculty_id.name}'

    @property
    def Subject_Dept(self):
        return f'{self.subject_id.dept_id.dept_name}'

    @property
    def Subject_Div(self):
        return f'{self.subject_id.div}'

    @property
    def Subject_Semester(self):
        return f'{self.subject_id.semester}'

    def __str__(self):
        return str(self.faculty_id) + " --> " + str(self.subject_id)


# Model to store questions of end semester feedback.
# Maximum 10 questions
class End_Sem_Feedback_Questions(models.Model):
    question_text = models.TextField()

    class Meta:
        verbose_name = "End Semester Feedback Question"
        verbose_name_plural = "End Semester Feedback Questions"

    def __str__(self):
        return self.question_text


# Model to store feedback for end semester
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
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE, verbose_name='Student')
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, verbose_name='Department')
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE, verbose_name='Subject')
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Faculty')
    semester = models.IntegerField('Semester', choices=SEMESTER, default=1)
    Q1 = models.IntegerField('Question 1', choices=RATINGS, default=0)
    Q2 = models.IntegerField('Question 2', choices=RATINGS, default=0)
    Q3 = models.IntegerField('Question 3', choices=RATINGS, default=0)
    Q4 = models.IntegerField('Question 4', choices=RATINGS, default=0)
    Q5 = models.IntegerField('Question 5', choices=RATINGS, default=0)
    Q6 = models.IntegerField('Question 6', choices=RATINGS, default=0)
    Q7 = models.IntegerField('Question 7', choices=RATINGS, default=0)
    Q8 = models.IntegerField('Question 8', choices=RATINGS, default=0)
    Q9 = models.IntegerField('Question 9', choices=RATINGS, default=0)
    Q10 = models.IntegerField('Question 10', choices=RATINGS, default=0)
    remarks = models.TextField('Remark', null=True, default=None)
    is_anonymous = models.BooleanField('Consent', default=False)
    timestamp = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        get_latest_by = ['timestamp']
        verbose_name = "End Semester Feedback"
        verbose_name_plural = "End Semester Feedback"

    @property
    def Feedback(self):
        return f'Feedback_{self.id}'

    @property
    def Faculty(self):
        return f'{self.faculty_id.name}'

    @property
    def Department(self):
        return f'{self.dept_id.accronym}'

    @property
    def Division(self):
        return f'{self.student_id.div}'

    @property
    def Subject(self):
        return f'{self.subject_id.subject_name} ({self.subject_id.subject_code})'


    def __str__(self):
        return f'Feedback_{self.id}'

    # def __str__(self):
    #     if int(self.student_id.semester) % 2:
    #         return "END_" + str(self.dept_id.accronym) + "_ODD_" + str(self.timestamp.year) + "_DIV_" + str(
    #             self.student_id.div) + "_" + str(self.subject_id.subject_code) + "_" + str(
    #             self.student_id.enrollment_no)[-3:]
    #     else:
    #         return "END_" + str(self.dept_id.accronym) + "_EVEN_" + str(self.timestamp.year) + "_DIV_" + str(
    #             self.student_id.div) + "_" + str(self.subject_id.subject_code) + "_" + str(
    #             self.student_id.enrollment_no)[-3:]


# Model to store mid semester feedback questions
# Maximum 10 questions
class Mid_Sem_Feedback_Questions(models.Model):
    question_text = models.TextField()

    class Meta:
        verbose_name = "Mid Semester Feedback Question"
        verbose_name_plural = "Mid Semester Feedback Questions"

    def __str__(self):
        return self.question_text


# Model to store Mid Semester Feedback
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
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE, verbose_name='Student')
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE, verbose_name='Department')
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE, verbose_name='Subject')
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Faculty')
    semester = models.IntegerField('Semester', choices=SEMESTER, default=1)
    Q1 = models.IntegerField('Question 1', choices=RATINGS, default=0)
    Q2 = models.IntegerField('Question 2', choices=RATINGS, default=0)
    Q3 = models.IntegerField('Question 3', choices=RATINGS, default=0)
    Q4 = models.IntegerField('Question 4', choices=RATINGS, default=0)
    Q5 = models.IntegerField('Question 5', choices=RATINGS, default=0)
    Q6 = models.IntegerField('Question 6', choices=RATINGS, default=0)
    Q7 = models.IntegerField('Question 7', choices=RATINGS, default=0)
    Q8 = models.IntegerField('Question 8', choices=RATINGS, default=0)
    Q9 = models.IntegerField('Question 9', choices=RATINGS, default=0)
    Q10 = models.IntegerField('Question 10', choices=RATINGS, default=0)
    remarks = models.TextField('Remark', null=True, default=None)
    is_anonymous = models.BooleanField('Consent', default=False)
    timestamp = models.DateTimeField('Date', auto_now_add=True)

    class Meta:
        get_latest_by = ['timestamp']
        verbose_name = "Mid Semester Feedback"
        verbose_name_plural = "Mid Semester Feedback"

    @property
    def Feedback(self):
        return f'Feedback_{self.id}'

    @property
    def Faculty(self):
        return f'{self.faculty_id.name}'

    @property
    def Department(self):
        return f'{self.dept_id.accronym}'

    @property
    def Division(self):
        return f'{self.student_id.div}'

    @property
    def Subject(self):
        return f'{self.subject_id.subject_name} ({self.subject_id.subject_code})'


    def __str__(self):
        return f'Feedback_{self.id}'

    # def __str__(self):
    #     if int(self.student_id.semester) % 2:
    #         return "MID_" + str(self.dept_id.accronym) + "_ODD_" + str(self.timestamp.year) + "_DIV_" + str(
    #             self.student_id.div) + "_" + str(self.subject_id.subject_code) + "_" + str(
    #             self.student_id.enrollment_no)[-3:]
    #     else:
    #         return "MID_" + str(self.dept_id.accronym) + "_EVEN_" + str(self.timestamp.year) + "_DIV_" + str(
    #             self.student_id.div) + "_" + str(self.subject_id.subject_code) + "_" + str(
    #             self.student_id.enrollment_no)[-3:]


# Model to store details of committee
class Committees(models.Model):
    committee_name = models.CharField('Committee Name', max_length=100)
    committee_details = models.TextField(verbose_name='Committee Detail')
    chairperson = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Chairperson')
    timestamp = models.DateTimeField('Date Added', auto_now_add=True)

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    def __str__(self):
        return self.committee_name


# Model for mapping of member s to committee
class Committee_to_Members_Mapping(models.Model):
    committee_id = models.ForeignKey(Committees, to_field='id', on_delete=models.CASCADE, verbose_name='Committee')
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Faculty')
    timestamp = models.DateTimeField('Date Added', auto_now_add=True)

    class Meta:
        verbose_name = "Committee to member mapping"
        verbose_name_plural = "Committee to member mapping"

    def __str__(self):
        return str(self.committee_id) + "->" + str(self.faculty_id)


# Model to store complaint information.
class Complaints(models.Model):
    STATUS = (
        ("Closed", "Closed"),
        ("Pending", "Pending"),
        ("Re-Opened", "Re-Opened"),
        ("Revoked", "Revoked"),
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE, verbose_name='Student')
    committee_id = models.ForeignKey(Committees, to_field='id', on_delete=models.CASCADE, verbose_name='Committee')
    complaint_details = models.TextField(verbose_name='Complaint')
    status = models.CharField('Status', max_length=30, choices=STATUS, default="Pending")
    reopened_count = models.IntegerField('Reopened count',
                                         default=0)  # 0 means first time complaints and 1 means first time reopened
    revoked = models.BooleanField('Is Revoked', default=False)
    revoked_reason = models.TextField('Reason of Revocation', null=True, blank=True)
    revoked_date = models.DateTimeField('Date of Revocation', null=True, blank=True)
    timestamp = models.DateTimeField('Date Added', auto_now_add=True)

    class Meta:
        verbose_name = "Student Complaints"
        verbose_name_plural = "Student Complaints"

    @property
    def Student(self):
        return f'{self.student_id.enrollment_no}'

    @property
    def Committee(self):
        return f'{self.committee_id.committee_name}'

    def __str__(self):
        return str(self.student_id.dept_id.accronym) + "_" + str(self.timestamp.year) + "_" + str(
            self.student_id.enrollment_no) + " -> " + self.status


# Model to store solution of complaints.
class Complaints_Solutions(models.Model):
    complaint_id = models.ForeignKey(Complaints, to_field='id', on_delete=models.CASCADE, verbose_name='Complaint')
    reopen_count = models.IntegerField('Complaint Reopen Count', default=0)  # for which complaint faculty reacted.
    reacting_faculty = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE,
                                         verbose_name='Committee Member')
    action = models.TextField(verbose_name='Action')
    timestamp = models.DateTimeField('Action taken date', auto_now_add=True)

    class Meta:
        verbose_name = "Solution of Student Complaints"
        verbose_name_plural = "Solution of Student Complaints"

    @property
    def Complaint(self):
        return f'Complaint_{self.complaint_id.id}'

    @property
    def Committee(self):
        return f'{self.complaint_id.committee_id.committee_name}'

    @property
    def Faculty(self):
        return f'{self.reacting_faculty.name}'

    def __str__(self):
        return str(self.reacting_faculty.name) + " -> " + str(self.complaint_id)


# Model to store why complaint has been reopened by student
class Complaint_Reopen_comments(models.Model):
    complaint_id = models.ForeignKey(Complaints, to_field='id', on_delete=models.CASCADE, verbose_name='Complaint')
    reopen_count = models.IntegerField(
        verbose_name='Reopen Count')  # it will start from one like first time reopened likewise.
    comments = models.TextField(verbose_name='Reopen Comment')
    timestamp = models.DateTimeField('Reopened Date', auto_now_add=True)

    class Meta:
        verbose_name = "Reopen Comments of student complaints"
        verbose_name_plural = "Reopen Comments of student complaints"

    @property
    def Complaint(self):
        return f'Complaint_{self.complaint_id.id}'

    @property
    def Committee(self):
        return f'{self.complaint_id.committee_id.committee_name}'

    def __str__(self):
        return str(self.complaint_id) + " > " + str(self.reopen_count) + " : " + str(self.comments)


# Model to store information of news published by faculties.
class News(models.Model):
    news_subject = models.TextField(verbose_name='News Heading')
    news_details = models.TextField(verbose_name='News')
    issuing_faculty = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Author Faculty')
    target_audience = models.ManyToManyField(Departments, verbose_name='Target Audience')
    timestamp = models.DateTimeField('Created Date', auto_now_add=True)

    class Meta:
        verbose_name = "News"
        verbose_name_plural = "News"

    @property
    def Faculty(self):
        return f'{self.issuing_faculty.name}'

    def __str__(self):
        return str(self.news_subject) + str(self.issuing_faculty)


# Model to store information whether student has given feedback for perticulat subject or not.
class Student_Feedback_Status(models.Model):
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE, verbose_name='Student')
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE, verbose_name='Subject')
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE, verbose_name='Faculty')
    # is_given = models.BooleanField(default=False)
    # end_sem_is_given = models.BooleanField(default=False)
    mid_sem_feedback = models.ForeignKey(Mid_Sem_Feedback_Answers, to_field='id', on_delete=models.CASCADE, null=True,
                                         verbose_name='Mid Semester Feedback')
    end_sem_feedback = models.ForeignKey(End_Sem_Feedback_Answers, to_field='id', on_delete=models.CASCADE, null=True,
                                         verbose_name='End Semester Feedback')
    timestamp = models.DateTimeField('Created Date', auto_now_add=True)

    class Meta:
        verbose_name = "Feedback Status of Students"
        verbose_name_plural = "Feedback Status of Students"

    @property
    def Mid_Sem_Feedback(self):
        if self.mid_sem_feedback:
            return f'Given'
        else:
            return 'Not Given'

    @property
    def End_Sem_Feedback(self):
        if self.end_sem_feedback:
            return f'Given'
        else:
            return 'Not Given'

    @property
    def Student(self):
        return f'{self.student_id.enrollment_no}'

    @property
    def Subject(self):
        return f'{self.subject_id.subject_name} ({self.subject_id.subject_code})'

    @property
    def Faculty(self):
        return f'{self.faculty_id.name}'

    def __str__(self):
        return f'Status_obj_{self.id}'

    # def __str__(self):
    #     return str(self.student_id.enrollment_no) + "_" + str(self.mid_sem_feedback) + "_" + str(self.end_sem_feedback)


class Issues(models.Model):
    name = models.CharField('Issuer Name', max_length=255)
    email = models.EmailField('Issuer Email', max_length=255)
    description = models.TextField(verbose_name='Issue')
    timestamp = models.DateTimeField('Created Date', auto_now_add=True)

    class Meta:
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    def __str__(self):
        return str(self.name) + str(self.description)
