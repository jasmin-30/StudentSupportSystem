# Generated by Django 2.2 on 2020-05-10 16:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0004_issues'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faculty',
            name='dept_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Departments'),
        ),
    ]
