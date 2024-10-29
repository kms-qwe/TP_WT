from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


QUESTIONS = [
    {
        'id': i,
        'title': f'Question {i}',
        'tags':  ['no' * (i%2) + 'hub', 'tag2', 'tag3'],
        'content': f'Content oxxxymiron is the smartest rapper {i}',
        'answers': [
            {
                'content': f'answer {j}',
                'likecount': f'{j*10}'
            } for j in range(10)
        ],
        'likecount': f'{i}'
    }   for i in range(200)
]


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
    page_obj = paginate(QUESTIONS, request) 
    return render(request, 'questionsListing.html', {'questions': page_obj})


def hot(request):
    hot_questions = sorted(QUESTIONS, key=lambda x: x.get("id"), reverse=True)
    page_obj = paginate(hot_questions, request) 
    return render(request, 'questionsListing.html', {'questions': page_obj})


def tag(request, tag_name):
    tag_questions = [q for q in QUESTIONS if tag_name in q.get("tags", [])]
    if not tag_questions:  
        raise Http404("No questions found for this tag.")
    page_obj = paginate(tag_questions, request) 

    return render(request, 'tagQuestionsListing.html', {'questions': page_obj})


def question(request, question_id):
    question = QUESTIONS[question_id]
    answers = question['answers']  
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