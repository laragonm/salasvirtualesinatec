# Generated by Django 3.2.4 on 2021-10-29 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solicitudes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructivo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visible', models.BooleanField(default=False)),
                ('archivo', models.FileField(upload_to='')),
            ],
            options={
                'verbose_name': 'instructivo',
            },
        ),
    ]
