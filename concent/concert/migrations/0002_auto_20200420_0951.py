# Generated by Django 3.0.5 on 2020-04-20 09:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('concert', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='concert',
            name='artists',
            field=models.ManyToManyField(to='concert.Artist', verbose_name='Artists in Concert'),
        ),
    ]