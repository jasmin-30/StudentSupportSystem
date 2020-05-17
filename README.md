# StudentSupportSystem
This is the project created to digitalize the traditional feedback taking system in college.
In School and colleges students are given feedback form through which they give feedback for faculties.
**Student Support System** provides a way by which this process can be done digitally.

It has Four user roles:
1. Student
2. Faculty
3. HOD (Head of department)
4. Principal

There are two feedback section one is **Mid Semester Feedback** which is taken in ongoing semester. 
and another one is **End Semester Feedback** which is taken after semester is over.

In this system Dashboards are designed as per user role and authorization of access.
Authorization of access means the Faculty can only see the feedback of subject which he/she is taking.
Head can see feedback reports of all the faculty under him/her. Principal can see feedback of all the faculties of college.

There is facility to download reports also. This report gives insights about how students reacted.
Faculty can also improve their performance according to feedback received.

Principal may have formed some committees for supporting students and resolving their issues and complaints.
Using this system student can also submit complaint and respective committee members can take action against complaint.

# Steps to run project
1. Create virtualenv using `virtualenv` command. `virtualenv venv`.
2. Once the virtualenvironemnt is created activate that virtual env by `activate`.
3. Install all the requirements from `requirements.txt` file using `pip install -r requirements.txt`.
4. Create database named `student_support_system`.
5. run `python manage.py migrate`.
6. Import `student_support_system.sql` file into created database to add necessary data.
7. after importing sql file you are good to go for runserver.

# Contributors
1. [Jasmin Makwana](https://github.com/jasmin-30)
2. [Jinesh Kamdar](https://github.com/JineshKamdar98)
3. [Kinjal Doshi](https://github.com/kd1398)
4. [Vishwa Rajput](https://github.com/VishwaRajput)
