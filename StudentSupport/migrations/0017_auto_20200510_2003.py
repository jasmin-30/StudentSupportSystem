# Generated by Django 2.2 on 2020-05-10 20:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('StudentSupport', '0016_auto_20200510_1950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee_to_members_mapping',
            name='committee_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Committees', verbose_name='Committee'),
        ),
        migrations.AlterField(
            model_name='committee_to_members_mapping',
            name='faculty_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty', verbose_name='Faculty'),
        ),
        migrations.AlterField(
            model_name='committee_to_members_mapping',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date Added'),
        ),
        migrations.AlterField(
            model_name='committees',
            name='chairperson',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='StudentSupport.Faculty', verbose_name='Chairperson'),
        ),
        migrations.AlterField(
            model_name='committees',
            name='committee_details',
            field=models.TextField(verbose_name='Committee Detail'),
        ),
        migrations.AlterField(
            model_name='committees',
            name='committee_name',
            field=models.CharField(max_length=100, verbose_name='Committee Name'),
        ),
        migrations.AlterField(
            model_name='committees',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Date Added'),
        ),
    ]
