import jwt
import time
from cent import Client, PublishRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Count
from .models import Question, Answer, Tag, QuestionLike, AnswerLike, User
from .forms import LoginForm, UserRegistrationForm, QuestionForm, AnswerForm, UserProfileEditForm
from django.urls import reverse
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from urllib.parse import urlparse
from django.conf import settings
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import Coalesce
from django.db import models
from django.core.cache import cache
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank


client = Client(settings.CENTRIFUGO_API_URL, api_key=settings.CENTRIFUGO_API_KEY, timeout=1)

def get_centrifugo_data(user_id, channel):
    return {
        "centrifugo": {
            "token": jwt.encode(
                {"sub": str(user_id), "exp":int(time.time()) + 10 * 60},
                settings.CENTRIFUGO_TOKEN_HMAC_SECRET_KEY,
                algorithm="HS256",
            ),
            "ws_url": settings.CENTRIFUGO_WS_URL,
            "channel": channel
        }
    }

def get_popular_tags():
    cache_key = 'popular_tags'
    popular_tags = cache.get(cache_key)
    return popular_tags

def set_cache_tags():
    cache_key = 'popular_tags'
    three_months_ago = timezone.now() - timedelta(days=90)

    popular_tags = Tag.objects.annotate(
        question_count=Count(
            'question',
            filter=models.Q(question__created_at__gte=three_months_ago)
        )
    ).filter(
        question_count__gt=0
    ).order_by(
        '-question_count'
    )[:5]

    cache.set(cache_key, popular_tags, timeout=10)



def get_best_users():
    cache_key = 'best_users'
    best_users = cache.get(cache_key)
    return best_users

def set_cache_users():
    cache_key = 'best_users'
    best_users = User.objects.annotate(
        total_likes=Count('questions__likes')
    ).filter(
        questions__isnull=False
    ).values('id', 'username', 'total_likes'
    ).order_by('-total_likes'
    ).distinct()[:5]

    cache.set(cache_key, best_users, timeout=10)  
    

def paginate(objects_list, request, per_page=5):
    page_number = request.GET.get('page', 1)
    paginator = Paginator(objects_list, per_page)

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return page_obj

def home(request):
    questions = Question.objects.filter_by_creation_time()
    page_obj = paginate(questions, request)
    popular_tags = get_popular_tags()
    best_users = get_best_users()
    return render(request, 'questionsListing.html', {
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_members': best_users
        })



def hot(request):
    questions = Question.objects.filter_by_likes()
    page_obj = paginate(questions, request)
    
    popular_tags = get_popular_tags()
    best_users = get_best_users()
    return render(request, 'questionsListing.html', {
        'questions': page_obj,
        'popular_tags': popular_tags,
        'best_members': best_users})


def tag(request, tag_name):
    questions = Question.objects.filter_by_tag(tag_name=tag_name).order_by('-created_at')  
    page_obj = paginate(questions, request)

    popular_tags = get_popular_tags()
    best_users = get_best_users()
    return render(request, 'tagQuestionsListing.html', {
        'questions': page_obj,
        'tag_name': tag_name,
        'popular_tags': popular_tags,
        'best_members': best_users
        })
 
def question(request, question_id):
    question = Question.objects.filter_by_id(question_id)
    answers = Answer.objects.for_question(question)
    
    page_answers = paginate(answers, request)

    popular_tags = get_popular_tags()
    best_users = get_best_users()
    
    form = AnswerForm()
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author_id = request.user.id
            answer.question_id = question.id
            answer.save()
            
            client.publish(PublishRequest(channel=f'question.{question_id}', data=model_to_dict(answer)))
            answer_index = list(answers).index(answer) + 1
            page = (answer_index - 1) // page_answers.paginator.per_page + 1

            return redirect(f"{request.path}?page={page}#answer-{answer.id}")

    is_author = request.user == question.author

    return render(request, 'questionPage.html', {
        'popular_tags': popular_tags,
        'best_members': best_users,
        'form': form,
        "question": question,
        "page_answers": page_answers,
        'is_author': is_author,
        **get_centrifugo_data(request.user.id, f'question.{question_id}')
        })




def login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)

                redirect_url = form.cleaned_data.get('next')

                if redirect_url:
                    parsed_url = urlparse(redirect_url)
                    if parsed_url.netloc in ('', 'localhost'):  
                        return redirect(redirect_url)

                return redirect(reverse('profile.edit'))
            form.add_error('password', 'Invalid username or password.')

    if 'next' in request.GET:
        form.fields['next'].initial = request.GET['next']

    return render(request, 'logInPage.html', {'form': form})


@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('home'))

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            auth.login(request, user)
            return redirect('home') 
    else:
        form = UserRegistrationForm()

    return render(request, 'registration.html', {'form': form})


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(user=request.user)
            return redirect(f'/question/{question.id}')
    else:
        form = QuestionForm()
    
    return render(request, 'newQuestion.html', {'form': form})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = UserProfileEditForm(
            request.POST, 
            request.FILES,  
            instance=request.user 
        )
        if form.is_valid():
            user = form.save()
            return redirect('profile.edit')
    else:
        form = UserProfileEditForm(instance=request.user)
    
    return render(request, 'userPage.html', {'form': form})

@login_required
def like_question(request):
    id = request.POST.get('question_id')
    question = get_object_or_404(Question, pk=id)
    QuestionLike.objects.toggle_like(user=request.user, question=question)  
    count = question.get_likes_count()

    return JsonResponse({
        'count': count
    })


@login_required
def like_answer(request):
    id = request.POST.get('answer_id')
    answer = get_object_or_404(Answer, pk=id)
    AnswerLike.objects.toggle_like(user=request.user, answer=answer)
    count = answer.get_likes_count()

    return JsonResponse({
        'count': count
    })

@login_required
def update_answer(request):
    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        is_correct = request.POST.get('is_correct') == 'true'
        
        try:
            answer = Answer.objects.get(id=answer_id)
            if request.user == answer.question.author:
                answer.is_correct = is_correct
                answer.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Not the author'})
        except Answer.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Answer not found'})


def search_questions(request):
    query = request.GET.get('q', '')
    if query:
        vector = SearchVector('title', weight='A') + SearchVector('text', weight='B')
        search_query = SearchQuery(query)
        
        questions = (
            Question.objects.annotate(rank=SearchRank(vector, search_query))
            .filter(rank__gte=0.1) 
            .order_by('-rank')[:10]
        )
        results = [{'title': q.title, 'id': q.id} for q in questions]
    else:
        results = []
    return JsonResponse(results, safe=False)