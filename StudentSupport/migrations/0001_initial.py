# Generated by Django 2.2 on 2020-04-29 12:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Departments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dept_name', models.CharField(max_length=100)),
                ('accronym', models.CharField(default=None, max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='End_Sem_Feedback_Answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], default=1)),
                ('Q1', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q2', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q3', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q4', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q5', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q6', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q7', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q8', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q9', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q10', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('remarks', models.TextField(default=None, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('dept_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments')),
            ],
            options={
                'get_latest_by': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='End_Sem_Feedback_Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Faculty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('hod', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Mid_Sem_Feedback_Answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], default=1)),
                ('Q1', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q2', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q3', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q4', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q5', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q6', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q7', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q8', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q9', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q10', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('remarks', models.TextField(default=None, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('dept_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments')),
                ('faculty_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
            ],
            options={
                'get_latest_by': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Mid_Sem_Feedback_Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Program_Exit_Survey_Questions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=255, unique=True)),
                ('role', models.CharField(blank=True, choices=[('Student', 'Student'), ('Faculty', 'Faculty'), ('Principal', 'Principal')], default='Student', max_length=20, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('password', models.CharField(max_length=255)),
                ('active', models.BooleanField(default=False)),
                ('staff', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
                ('requested_change_password', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject_name', models.CharField(max_length=255)),
                ('subject_code', models.CharField(max_length=10)),
                ('semester', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], default=1)),
                ('is_active', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('dept_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments')),
            ],
        ),
        migrations.CreateModel(
            name='Subject_to_Faculty_Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('faculty_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Subjects')),
            ],
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('enrollment_no', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('div', models.IntegerField(choices=[(1, 1), (2, 2)], default=1)),
                ('semester', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8)], default=1)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('auth_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('dept_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='StudentSupport.Departments')),
            ],
        ),
        migrations.CreateModel(
            name='Student_Feedback_Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('end_sem_feedback', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.End_Sem_Feedback_Answers')),
                ('faculty_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
                ('mid_sem_feedback', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Mid_Sem_Feedback_Answers')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Students')),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Subjects')),
            ],
        ),
        migrations.CreateModel(
            name='Program_Exit_Survey_Answers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Q1', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q2', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q3', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q4', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q5', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q6', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q7', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q8', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q9', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('Q10', models.IntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], default=0)),
                ('remarks', models.TextField(null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('dept_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Students')),
            ],
        ),
        migrations.CreateModel(
            name='Principal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('auth_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='News',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('news_subject', models.TextField()),
                ('news_details', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('issuing_faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
                ('target_audience', models.ManyToManyField(to='StudentSupport.Departments')),
            ],
        ),
        migrations.AddField(
            model_name='mid_sem_feedback_answers',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Students'),
        ),
        migrations.AddField(
            model_name='mid_sem_feedback_answers',
            name='subject_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Subjects'),
        ),
        migrations.AddField(
            model_name='faculty',
            name='auth_id',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='faculty',
            name='dept_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments'),
        ),
        migrations.AddField(
            model_name='end_sem_feedback_answers',
            name='faculty_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty'),
        ),
        migrations.AddField(
            model_name='end_sem_feedback_answers',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Students'),
        ),
        migrations.AddField(
            model_name='end_sem_feedback_answers',
            name='subject_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Subjects'),
        ),
        migrations.CreateModel(
            name='Committees',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('committee_name', models.CharField(max_length=100)),
                ('committee_details', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('chairperson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
            ],
        ),
        migrations.CreateModel(
            name='Committee_to_Members_Mapping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('committee_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Committees')),
                ('faculty_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty')),
            ],
        ),
    ]
