from django.db import models
from django.conf import settings

# Create your models here.

# Models to store information about all the departments.
class Departments(models.Model):
    dept_name = models.CharField(max_length = 100)
    accronym = models.CharField(max_length=5, default=None)

    def __str__(self):
        return self.dept_name

class Principal(models.Model):
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default = None)

    def __str__(self):
        return str(self.auth_id)

class Faculty(models.Model):
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default = None)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.auth_id)


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
    auth_id = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE, default = None)
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
    subject_name = models.CharField(max_length=100)
    subject_code = models.CharField(max_length=10, unique=True)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject_name

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
    Q1 = models.IntegerField(choices=RATINGS, default=1)
    Q2 = models.IntegerField(choices=RATINGS, default=1)
    Q3 = models.IntegerField(choices=RATINGS, default=1)
    Q4 = models.IntegerField(choices=RATINGS, default=1)
    Q5 = models.IntegerField(choices=RATINGS, default=1)
    Q6 = models.IntegerField(choices=RATINGS, default=1)
    Q7 = models.IntegerField(choices=RATINGS, default=1)
    Q8 = models.IntegerField(choices=RATINGS, default=1)
    Q9 = models.IntegerField(choices=RATINGS, default=1)
    Q10 = models.IntegerField(choices=RATINGS, default=1)
    remarks = models.TextField()
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
    Q1 = models.IntegerField(choices=RATINGS, default=1)
    Q2 = models.IntegerField(choices=RATINGS, default=1)
    Q3 = models.IntegerField(choices=RATINGS, default=1)
    Q4 = models.IntegerField(choices=RATINGS, default=1)
    Q5 = models.IntegerField(choices=RATINGS, default=1)
    Q6 = models.IntegerField(choices=RATINGS, default=1)
    Q7 = models.IntegerField(choices=RATINGS, default=1)
    Q8 = models.IntegerField(choices=RATINGS, default=1)
    Q9 = models.IntegerField(choices=RATINGS, default=1)
    Q10 = models.IntegerField(choices=RATINGS, default=1)
    remarks = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id)


class Course_Exit_Survey_Questions(models.Model):
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
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
    faculty_id = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    question_text = models.TextField()
    semester = models.IntegerField(choices=SEMESTER, default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.faculty_id)

class Course_Exit_Survey_Answers(models.Model):
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
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    subject_id = models.ForeignKey(Subjects, to_field='id', on_delete=models.CASCADE)
    survey_id = models.ForeignKey(Course_Exit_Survey_Questions, to_field='id', on_delete=models.CASCADE)
    semester = models.IntegerField(choices=SEMESTER, default=1)
    Q1 = models.IntegerField(choices=RATINGS, default=1)
    Q2 = models.IntegerField(choices=RATINGS, default=1)
    Q3 = models.IntegerField(choices=RATINGS, default=1)
    Q4 = models.IntegerField(choices=RATINGS, default=1)
    Q5 = models.IntegerField(choices=RATINGS, default=1)
    remarks = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.student_id)+str(self.survey_id)


class Program_Exit_Survey_Questions(models.Model):
    question_text = models.TextField()

    def __str__(self):
        return self.question_text


class Program_Exit_Survey_Answers(models.Model):
    RATINGS = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    student_id = models.ForeignKey(Students, to_field='enrollment_no', on_delete=models.CASCADE)
    dept_id = models.ForeignKey(Departments, to_field='id', on_delete=models.CASCADE)
    Q1 = models.IntegerField(choices=RATINGS, default=1)
    Q2 = models.IntegerField(choices=RATINGS, default=1)
    Q3 = models.IntegerField(choices=RATINGS, default=1)
    Q4 = models.IntegerField(choices=RATINGS, default=1)
    Q5 = models.IntegerField(choices=RATINGS, default=1)
    Q6 = models.IntegerField(choices=RATINGS, default=1)
    Q7 = models.IntegerField(choices=RATINGS, default=1)
    Q8 = models.IntegerField(choices=RATINGS, default=1)
    Q9 = models.IntegerField(choices=RATINGS, default=1)
    Q10 = models.IntegerField(choices=RATINGS, default=1)
    remarks = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
            return str(self.student_id)

class Committee_Details(models.Model):
    committee_name = models.CharField(max_length=100)
    committee_details = models.TextField()
    chairperson = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE)
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
    reacting_faculty = models.ForeignKey(settings.AUTH_USER_MODEL, to_field='id', on_delete=models.CASCADE)
    action_taken = models.TextField()
    report = models.TextField()
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
        (9, 9)#9 means all departments
    )
    news_details = models.TextField()
    issuing_faculty = models.ForeignKey(Faculty, to_field='id', on_delete=models.CASCADE)
    target_audience = models.CharField(max_length=2, choices=SEMESTER, default=9)
    start_date = models.DateField(auto_now_add=True)
    expiry_date = models.DateField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.news_details