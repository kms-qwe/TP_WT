from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from ...models import (
    Profile, Question, Answer, Tag, 
    TagQuestion, QuestionLike, AnswerLike
)

class Command(BaseCommand):
    help = 'Deletes all data from database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help='Delete without confirmation'
        )

    def handle(self, *args, **options):
        if not options['no_confirm']:
            confirm = input(
                'This will delete ALL DATA from the database. Are you sure? (y/N): '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        try:
            with transaction.atomic():
                
                self.stdout.write('Deleting likes...')
                QuestionLike.objects.all().delete()
                AnswerLike.objects.all().delete()

                self.stdout.write('Deleting tag relations...')
                TagQuestion.objects.all().delete()

                self.stdout.write('Deleting questions and answers...')
                Question.objects.all().delete()
                Answer.objects.all().delete()

                self.stdout.write('Deleting tags...')
                Tag.objects.all().delete()

                self.stdout.write('Deleting user profiles...')
                Profile.objects.all().delete()

                self.stdout.write('Deleting users...')
                User.objects.exclude(is_superuser=True).delete() 
                self.stdout.write(
                    self.style.SUCCESS('Successfully deleted all data.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error occurred while deleting data: {str(e)}')
            )
            raise