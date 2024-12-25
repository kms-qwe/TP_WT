from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models
import django.contrib.postgres.search

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_alter_question_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(null=True),
        ),
        migrations.AddIndex(
            model_name='question',
            index=GinIndex(
                fields=['search_vector'],
                name='question_search_vector_gin'  
            ),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(upload_to='img/avatars/'),
        ),
        migrations.AlterField(
            model_name='question',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
