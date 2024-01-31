# Generated by Django 5.0.1 on 2024-01-25 18:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='color',
            field=models.CharField(choices=[('cool_white', 'Cool White'), ('warm-white', 'Warm White'), ('yellow', 'Yellow'), ('orange', 'Orange'), ('red', 'Red'), ('pink', 'Pink'), ('hot_pink', 'Hot Pink'), ('purple', 'Purple'), ('blue', 'Blue'), ('ice_blue', 'Ice Blue'), ('green', 'Green'), ('custom', 'Custom Colors')], max_length=255),
        ),
        migrations.AlterField(
            model_name='order',
            name='cut_type',
            field=models.CharField(choices=[('cut_to_shape', 'Cut to Shape'), ('square_rectangle', 'Square/Rectangle'), ('cut_to_letter', 'Cut to Letter'), ('circular_round', 'Circular/Round')], max_length=255),
        ),
    ]
