# Generated by Django 4.2.8 on 2024-01-27 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('Stocks', '0015_remove_stockdata_ema_remove_stockdata_rs_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='bio',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='birth_date',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='user_profiles_groups', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_profiles_permissions', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
