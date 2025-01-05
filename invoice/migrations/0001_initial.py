# Generated by Django 3.2.25 on 2025-01-05 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.IntegerField(unique=True)),
                ('client_name', models.CharField(max_length=255)),
                ('client_email', models.EmailField(max_length=254)),
                ('client_address', models.TextField()),
                ('registration_code', models.CharField(max_length=255)),
                ('due_date', models.DateField()),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]