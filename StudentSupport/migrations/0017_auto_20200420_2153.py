# Generated by Django 2.2 on 2020-04-20 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0016_auto_20200416_0210'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mid_sem_feedback_answers',
            options={'get_latest_by': ['timestamp']},
        ),
        migrations.AlterField(
            model_name='end_sem_feedback_answers',
            name='remarks',
            field=models.TextField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='mid_sem_feedback_answers',
            name='remarks',
            field=models.TextField(default=None, null=True),
        ),
    ]