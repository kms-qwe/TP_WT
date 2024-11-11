from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files import File
from django.conf import settings
from django.db import transaction
from django.contrib.auth.hashers import make_password
from django.core.files import File
import random
from datetime import timedelta
from faker import Faker
from app.models import (
    Profile, Question, Answer, Tag, 
    TagQuestion, QuestionLike, AnswerLike
)

fake = Faker()

class Command(BaseCommand):
    help = 'Fills database with sample data based on ratio coefficient'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            help='Ratio coefficient for database population'
        )

    def handle(self, *args, **options):
        ratio = options['ratio']
        
        num_users = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_tags = ratio
        num_likes = ratio * 200

        self.stdout.write(f'Starting database population with ratio {ratio}')
        self.stdout.write(f'Users to create: {num_users}')
        self.stdout.write(f'Questions to create: {num_questions}')
        self.stdout.write(f'Answers to create: {num_answers}')
        self.stdout.write(f'Tags to create: {num_tags}')
        self.stdout.write(f'Likes to distribute: {num_likes}')

        try:
            with transaction.atomic():
                self.stdout.write('Creating users...')
                users = self._create_users(num_users)
                
                self.stdout.write('Creating tags...')
                tags = self._create_tags(num_tags)
                
                self.stdout.write('Creating questions...')
                questions = self._create_questions(num_questions, users, tags)
                
                self.stdout.write('Creating answers...')
                answers = self._create_answers(num_answers, users, questions)
                
                self.stdout.write('Creating likes...')
                self._create_likes(num_likes, users, questions, answers)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error occurred while creating data: {str(e)}')
            )
            raise
        
        self.stdout.write(self.style.SUCCESS(f'Successfully filled database with ratio {ratio}'))


    def _create_users(self, count):
        users_to_create = []
        chunk_size = 5000
        
        usernames = set()
        user_data = []
        
        while len(user_data) < count:
            username = fake.user_name()
            if username not in usernames:
                usernames.add(username)
                user_data.append((
                    username,
                    fake.email(),
                    fake.first_name(),
                    fake.last_name()
                ))
        
        created_users = []
        for i in range(0, count, chunk_size):
            chunk_end = min(i + chunk_size, count)
            chunk_users = [
                User(
                    username=data[0],
                    email=data[1],
                    first_name=data[2],
                    last_name=data[3]
                )
                for data in user_data[i:chunk_end]
            ]
            created_users.extend(
                User.objects.bulk_create(chunk_users)
            )
        
        current_time = timezone.now()
        for i in range(0, len(created_users), chunk_size):
            chunk_end = min(i + chunk_size, len(created_users))
            profiles_to_create = [
                Profile(user=user, created_at=current_time)
                for user in created_users[i:chunk_end]
            ]
            Profile.objects.bulk_create(profiles_to_create)
        
        return created_users

    def _create_tags(self, count):
        tags_to_create = []
        unique_tags = set()
        chunk_size = 5000
        
        words = [fake.word()[:10] for _ in range(count * 2)]  
        numbers = [str(random.randint(1000000000, 9999999999)) for _ in range(count * 2)]
        
        i = 0
        while len(unique_tags) < count and i < len(words):
            tag_name = f"{words[i]}{numbers[i]}"
            if tag_name not in unique_tags:
                unique_tags.add(tag_name)
            i += 1
        
        created_tags = []
        tags_list = list(unique_tags)
        
        for i in range(0, count, chunk_size):
            chunk_end = min(i + chunk_size, count)
            chunk_tags = [
                Tag(tag_name=tag_name)
                for tag_name in tags_list[i:chunk_end]
            ]
            created_tags.extend(
                Tag.objects.bulk_create(chunk_tags)
            )
        
        return created_tags

    def _create_questions(self, count, users, tags):
        questions_to_create = []
        tag_questions_to_create = []
        chunk_size = 5000
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=365)
        
        dates = [
            timezone.make_aware(
                fake.date_time_between_dates(start_date, end_date)
            )
            for _ in range(count)
        ]
        titles = [fake.sentence(nb_words=6)[:-1] for _ in range(count)]
        texts = [fake.text(max_nb_chars=1000) for _ in range(count)]
        authors = random.choices(users, k=count)
        
        created_questions = []
        for i in range(0, count, chunk_size):
            chunk_end = min(i + chunk_size, count)
            chunk_questions = [
                Question(
                    title=titles[j],
                    text=texts[j],
                    author=authors[j],
                    created_at=dates[j]
                )
                for j in range(i, chunk_end)
            ]
            created_questions.extend(
                Question.objects.bulk_create(chunk_questions)
            )
        
        tags_list = list(tags)
        tags_counts = [random.randint(1, min(3, len(tags_list))) for _ in range(len(created_questions))]
        
        tag_selections = [
            random.sample(tags_list, k=tag_count)
            for tag_count in tags_counts
        ]
        
        for i, question in enumerate(created_questions):
            tag_questions_to_create.extend([
                TagQuestion(tag=tag, question=question)
                for tag in tag_selections[i]
            ])
            
            if len(tag_questions_to_create) >= chunk_size:
                TagQuestion.objects.bulk_create(tag_questions_to_create, ignore_conflicts=True)
                tag_questions_to_create = []
        
        if tag_questions_to_create:
            TagQuestion.objects.bulk_create(tag_questions_to_create, ignore_conflicts=True)
        
        return created_questions

    def _create_answers(self, count, users, questions):
        answers_to_create = []
        chunk_size = 5000
        end_date = timezone.now()
        
        texts = [fake.text(max_nb_chars=500) for _ in range(count)]
        is_correct_list = [random.random() < 0.1 for _ in range(count)]
        authors = random.choices(users, k=count)
        selected_questions = random.choices(questions, k=count)
        
        dates = [
            timezone.make_aware(
                fake.date_time_between_dates(
                    question.created_at,
                    end_date
                )
            )
            for question in selected_questions
        ]
        
        created_answers = []
        for i in range(0, count, chunk_size):
            chunk_end = min(i + chunk_size, count)
            chunk_answers = [
                Answer(
                    text=texts[j],
                    is_correct=is_correct_list[j],
                    author=authors[j],
                    question=selected_questions[j],
                    created_at=dates[j]
                )
                for j in range(i, chunk_end)
            ]
            created_answers.extend(
                Answer.objects.bulk_create(chunk_answers)
            )
        
        return created_answers

    def _create_likes(self, count, users, questions, answers):
        chunk_size = 5000
        question_likes_count = int(count * 0.4)
        answer_likes_count = count - question_likes_count
        
        question_pairs = set()
        question_likes_to_create = []
        
        user_ids = [user.id for user in users]
        question_ids = [question.id for question in questions]
        
        while len(question_likes_to_create) < question_likes_count:
            user_id = random.choice(user_ids)
            question_id = random.choice(question_ids)
            pair = (user_id, question_id)
            
            if pair not in question_pairs:
                question_pairs.add(pair)
                question_likes_to_create.append(
                    QuestionLike(
                        user_id=user_id,
                        question_id=question_id
                    )
                )
        
        for i in range(0, len(question_likes_to_create), chunk_size):
            chunk_end = min(i + chunk_size, len(question_likes_to_create))
            QuestionLike.objects.bulk_create(
                question_likes_to_create[i:chunk_end],
                ignore_conflicts=True
            )
        
        answer_pairs = set()
        answer_likes_to_create = []
        answer_ids = [answer.id for answer in answers]
        
        while len(answer_likes_to_create) < answer_likes_count:
            user_id = random.choice(user_ids)
            answer_id = random.choice(answer_ids)
            pair = (user_id, answer_id)
            
            if pair not in answer_pairs:
                answer_pairs.add(pair)
                answer_likes_to_create.append(
                    AnswerLike(
                        user_id=user_id,
                        answer_id=answer_id
                    )
                )
        
        for i in range(0, len(answer_likes_to_create), chunk_size):
            chunk_end = min(i + chunk_size, len(answer_likes_to_create))
            AnswerLike.objects.bulk_create(
                answer_likes_to_create[i:chunk_end],
                ignore_conflicts=True
            )
        
        return question_likes_to_create, answer_likes_to_create