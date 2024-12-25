from django.core.management.base import BaseCommand
from app.views import set_cache_users, set_cache_tags

class Command(BaseCommand):
    help = 'Заполняет кэш для популярных тегов и лучших пользователей'

    def handle(self, *args, **kwargs):
        set_cache_users()
        set_cache_tags()
        self.stdout.write(self.style.SUCCESS('Кэш был успешно заполнен!'))
