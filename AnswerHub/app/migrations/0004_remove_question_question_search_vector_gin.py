# Generated by Django 4.2.17 on 2024-12-25 18:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_question_search_vector_alter_profile_avatar_and_more'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='question',
            name='question_search_vector_gin',
        ),
    ]
