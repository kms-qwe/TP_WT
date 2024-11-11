from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Count
from .models import Question, Answer, Tag

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
    
    return render(request, 'questionPage.html', {
        "question": question,
        "page_answers": page_answers 
    })




def login(request):
    return render(request, 'logInPage.html')


def signup(request):
    return render(request, 'registration.html')


def ask(request):
    return render(request, 'newQuestion.html')


def settings(request):
    return render(request, 'userPage.html')