# Generated by Django 4.2.3 on 2023-09-19 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vapp', '0014_alter_userprofile_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(blank=True, default='default.webp', null=True, upload_to='media/profile_photos/'),
        ),
    ]
