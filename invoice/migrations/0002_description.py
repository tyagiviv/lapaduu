# Generated by Django 3.2.25 on 2025-01-05 20:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Description',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='descriptions', to='invoice.invoice')),
            ],
        ),
    ]
