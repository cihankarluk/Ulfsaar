# Generated by Django 2.2.7 on 2020-08-26 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_auto_20200818_1541'),
    ]

    operations = [
        migrations.AddField(
            model_name='searcherrortracks',
            name='provider',
            field=models.CharField(choices=[('spotify', 'spotify'), ('youtube', 'youtube')], max_length=64),
            preserve_default=False,
        ),
    ]