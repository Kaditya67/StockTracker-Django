# Generated by Django 5.0.3 on 2024-03-26 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stocks', '0032_remove_stock_user_watchlist_stock'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock_user',
            name='email',
            field=models.EmailField(max_length=254),
        ),
    ]
