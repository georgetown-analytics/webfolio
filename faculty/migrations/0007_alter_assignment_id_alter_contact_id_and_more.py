# Generated by Django 4.1.3 on 2022-11-19 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("faculty", "0006_auto_20210204_1210"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assignment",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="contact",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="faculty",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]