# Generated by Django 5.1.2 on 2024-10-14 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_remove_userprofile_email_remove_userprofile_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to='profile_pictures/'),
        ),
    ]