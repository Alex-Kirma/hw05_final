# Generated by Django 2.2.6 on 2022-01-19 22:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0016_auto_20220119_2342'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
    ]