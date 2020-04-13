# Generated by Django 2.2 on 2020-04-07 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0008_auto_20200327_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaints_of_students',
            name='action_taken',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='complaints_of_students',
            name='reacting_faculty',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='complaints_of_students',
            name='report',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Student_Feedback_Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_given', models.BooleanField(default=False)),
                ('end_sem_is_given', models.BooleanField(default=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Students')),
                ('subject_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Subjects')),
            ],
        ),
    ]
