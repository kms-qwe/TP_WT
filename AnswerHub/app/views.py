from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Count
from .models import Question, Answer, Tag
from .forms import LoginForm, UserRegistrationForm, QuestionForm, AnswerForm, UserProfileEditForm
from django.urls import reverse
from django.contrib import auth
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

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
    return render(request, 'questionsListing.html', {'questions': page_obj})



def hot(request):
    questions = Question.objects.filter_by_likes()
    page_obj = paginate(questions, request)
    return render(request, 'questionsListing.html', {'questions': page_obj})


def tag(request, tag_name):
    questions = Question.objects.filter_by_tag(tag_name=tag_name).order_by('-created_at')  
    page_obj = paginate(questions, request)
    return render(request, 'tagQuestionsListing.html', {
        'questions': page_obj,
        'tag_name': tag_name
        })
 
def question(request, question_id):
    question = Question.objects.filter_by_id(question_id)
    answers = Answer.objects.for_question(question)
    
    page_answers = paginate(answers, request)
    
    form = AnswerForm()
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author_id = request.user.id
            answer.question_id = question.id
            answer.save()
            return redirect('question', question_id=question.id)
            
    return render(request, 'questionPage.html', {
        'form': form,
        "question": question,
        "page_answers": page_answers 
    })




def login(request):
    form = LoginForm
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user:
                auth.login(request, user)
                return redirect(reverse('profile.edit'))
            form.add_error('password', 'Invalid username or password.')

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


