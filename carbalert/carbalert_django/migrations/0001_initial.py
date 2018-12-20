# Generated by Django 2.1.3 on 2018-12-19 10:20

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchPhrase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phrase', models.CharField(blank=True, max_length=100)),
                ('email_users', models.ManyToManyField(related_name='email_users', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('thread_id', models.CharField(blank=True, max_length=20)),
                ('title', models.CharField(blank=True, max_length=200)),
                ('url', models.CharField(blank=True, max_length=200)),
                ('text', models.TextField(max_length=1000)),
                ('datetime', models.DateTimeField(blank=True)),
                ('search_phrases', models.ManyToManyField(to='carbalert_django.SearchPhrase')),
            ],
        ),
    ]