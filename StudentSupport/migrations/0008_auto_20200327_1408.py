# Generated by Django 2.2 on 2020-03-27 08:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0007_faculty_hod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='dept_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments'),
        ),
    ]
