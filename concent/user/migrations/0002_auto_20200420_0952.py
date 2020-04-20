# Generated by Django 3.0.5 on 2020-04-20 09:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concert', '0002_auto_20200420_0951'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='artists',
            field=models.ManyToManyField(to='concert.Artist', verbose_name='Bookmarked Artists'),
        ),
        migrations.AddField(
            model_name='user',
            name='concerts',
            field=models.ManyToManyField(to='concert.Concert', verbose_name='Bookmarked Concerts'),
        ),
    ]