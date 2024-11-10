from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/')
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)      

    def __str__(self):
        return f"{self.user.username}'s Profile"


class QuestionManager(models.Manager):
    def filter_by_creation_time(self, start_time=None, end_time=None):
        queryset = self.all().annotate(likeCount=Count('likes'))

        if start_time and end_time:
            queryset = queryset.filter(created_at__range=[start_time, end_time])
        elif start_time:
            queryset = queryset.filter(created_at__gte=start_time)
        elif end_time:
            queryset = queryset.filter(created_at__lte=end_time)
        
        return queryset

    def filter_by_likes(self):
        queryset = self.annotate(likeCount=Count('likes'))
        return queryset.order_by('-likeCount')

    
    def filter_by_tag(self, tag_name):
        return self.filter(tags__tag_name=tag_name).annotate(likeCount=Count('likes')).distinct()


    def filter_by_id(self, id):
        try:
            return self.annotate(likeCount=Count('likes')).get(id=id)
        except ObjectDoesNotExist:
            return None 




class AnswerManager(models.Manager):
   def for_question(self, question=None):
    one_week_ago = timezone.now() - timedelta(days=7)
    queryset = self.filter(question=question, created_at__gte=one_week_ago)
    queryset = queryset.annotate(likeCount=Count('likes'))
    return queryset.order_by('-is_correct', '-likeCount')
    


class Question(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField('Tag', through='TagQuestion')
    objects = QuestionManager() 
    def __str__(self):
        return self.title


class Answer(models.Model):
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AnswerManager() 

    def __str__(self):
        return f"Answer by {self.author.username}"


class Tag(models.Model):
    tag_name = models.CharField(max_length=20)

    def __str__(self):
        return self.tag_name


class TagQuestion(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('tag', 'question')


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_likes')

    class Meta:
        unique_together = ('question', 'user')


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_likes')

    class Meta:
        unique_together = ('answer', 'user')
