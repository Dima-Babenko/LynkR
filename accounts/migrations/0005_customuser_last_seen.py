# Generated by Django 5.2.1 on 2025-06-01 18:06

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_alter_customuser_friend_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='last_seen',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
