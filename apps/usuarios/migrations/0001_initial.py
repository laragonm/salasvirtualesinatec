# Generated by Django 3.2.4 on 2021-07-09 20:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Perfil',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_area', models.CharField(blank=True, max_length=8)),
                ('id_direccion', models.CharField(blank=True, max_length=4)),
                ('id_centro', models.CharField(blank=True, max_length=4)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='perfil', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'perfiles',
                'ordering': ['usuario'],
            },
        ),
    ]
