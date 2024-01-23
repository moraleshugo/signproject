# Generated by Django 5.0.1 on 2024-01-16 18:17

import django.db.models.deletion
import orders.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='customer_notes',
        ),
        migrations.RemoveField(
            model_name='order',
            name='image',
        ),
        migrations.AddField(
            model_name='order',
            name='process_status',
            field=models.CharField(choices=[('new', 'New Order'), ('to_do', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')], default='new', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.CharField(blank=True, choices=[('New Order', 'New Order'), ('In Progress', 'In Progress'), ('Needs Design', 'Needs Design'), ('Design Ready', 'Design Ready'), ('Pending Approval', 'Pending Approval'), ('Approved', 'Approved'), ('Shipped', 'Shipped'), ('Cancelled', 'Cancelled'), ('Awaits Pickup', 'Awaits Pickup'), ('Delivered', 'Delivered'), ('Complete', 'Complete')], max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.PositiveIntegerField(blank=True, default=1, null=True),
        ),
        migrations.CreateModel(
            name='OrderImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_images', models.ImageField(blank=True, null=True, upload_to=orders.models.order_image_path)),
                ('original_file_name', models.CharField(blank=True, max_length=255, null=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
            ],
        ),
    ]