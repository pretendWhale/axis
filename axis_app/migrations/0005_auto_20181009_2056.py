# Generated by Django 2.1.2 on 2018-10-09 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('axis_app', '0004_explanation_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='explanation',
            name='added_to_version_set',
            field=models.BooleanField(blank=True, null=True),
        ),
    ]
