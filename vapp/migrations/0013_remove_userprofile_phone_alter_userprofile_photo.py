# Generated by Django 4.2.3 on 2023-09-19 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vapp', '0012_userprofile_date_created_userprofile_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='phone',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(blank=True, default='media/profile_photos/default.webp', upload_to='media/profile_photos/'),
        ),
    ]