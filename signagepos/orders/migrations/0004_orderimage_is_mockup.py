# Generated by Django 5.0.1 on 2024-01-20 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_alter_order_customer'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderimage',
            name='is_mockup',
            field=models.BooleanField(default=False),
        ),
    ]
