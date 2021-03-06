# Generated by Django 2.2.4 on 2019-09-04 16:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscourseClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forum_url', models.URLField()),
                ('api_key', models.CharField(max_length=255)),
                ('api_username', models.CharField(max_length=255)),
                ('sso_secret', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='DiscourseGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('external_id', models.BigIntegerField(unique=True)),
                ('group', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discourse_group', to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='DiscourseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.BigIntegerField(unique=True)),
                ('username', models.CharField(max_length=255)),
                ('groups', models.ManyToManyField(blank=True, to='django_discourse_connector.DiscourseGroup')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='discourse_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
