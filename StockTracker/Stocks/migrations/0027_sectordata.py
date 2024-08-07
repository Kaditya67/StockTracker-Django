# Generated by Django 5.0.1 on 2024-02-07 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Stocks', '0026_emacounts_rs_output_emacounts_rsi_output'),
    ]

    operations = [
        migrations.CreateModel(
            name='SectorData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(max_length=10)),
                ('date', models.DateField()),
                ('close_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('ema20', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ema50', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ema100', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('ema200', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rsi', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rs', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
    ]
