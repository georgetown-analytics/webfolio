# Generated by Django 3.0.1 on 2019-12-30 05:07

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Capstone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('title', models.CharField(help_text='The full title of the capstone project', max_length=255)),
            ],
            options={
                'db_table': 'capstones',
                'ordering': ('-cohort',),
            },
        ),
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('cohort', models.PositiveSmallIntegerField(help_text='The cohort number, e.g. which cohort from the beginning of the program', unique=True)),
                ('semester', models.CharField(choices=[('SP', 'Spring'), ('SU', 'Summer'), ('FA', 'Fall')], help_text='The academic semester the cohort has been assigned to', max_length=2)),
                ('section', models.CharField(blank=True, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], default=None, help_text='If multiple cohorts per semester, the semester section', max_length=1, null=True)),
                ('start', models.DateField(blank=True, default=None, help_text='Date that the cohort starts, e.g. the first day of Foundations', null=True)),
                ('end', models.DateField(blank=True, default=None, help_text='Date that the cohort ends, e.g. the last day of Applied', null=True)),
            ],
            options={
                'db_table': 'cohorts',
                'ordering': ('-cohort',),
            },
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('course_id', models.CharField(db_index=True, help_text='The course ID, e.g. XBUS-500 that uniquely identifies an offering', max_length=55, verbose_name='Course ID')),
                ('section', models.PositiveSmallIntegerField(help_text='The course section, should be unique with course_id')),
                ('title', models.CharField(help_text="The full title of the course in the semester it's offered", max_length=255)),
                ('hours', models.PositiveSmallIntegerField(blank=True, default=12, help_text='The number of hours in the course, e.g. the CEUs', null=True)),
                ('start', models.DateField(blank=True, help_text='Date that the course starts, e.g. the first day of of the course', null=True)),
                ('end', models.DateField(blank=True, help_text='Date that the course ends, e.g. the last day of the course', null=True)),
                ('cohort', models.ForeignKey(help_text='The cohort taking this course', on_delete=django.db.models.deletion.CASCADE, related_name='courses', to='cohort.Cohort')),
            ],
            options={
                'db_table': 'courses',
                'ordering': ('-cohort__cohort', 'start'),
            },
        ),
    ]
