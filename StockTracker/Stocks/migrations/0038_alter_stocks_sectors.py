# Generated by Django 5.0.3 on 2024-05-02 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stocks', '0037_alter_stocks_sectors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stocks',
            name='sectors',
            field=models.ManyToManyField(to='Stocks.sectors'),
        ),
    ]
