# Generated by Django 4.2.3 on 2023-09-16 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vapp', '0007_alter_userprofile_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phonenumber',
            field=models.CharField(default=None, max_length=10),
        ),
    ]