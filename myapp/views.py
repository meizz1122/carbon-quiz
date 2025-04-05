from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import uuid

from django.db.models import F
from django.urls import reverse

from .models import Question, Choice, Quiz_Question, Quiz_Choice, Quiz_User, Quiz_Response


#A view is a “type” of web page in your Django application that generally serves a specific function and has a specific template
#views return HttpResponse
#In Django, web pages and other content are delivered by views. Each view is represented by a Python function (or method, in the case of class-based views). 
#Django will choose a view by examining the URL that’s requested (to be precise, the part of the URL after the domain name).

#to access view in a browser, we need to map it to a URL - and for this we need to define a URL configuration, 
#or “URLconf” for short. These URL configurations are defined inside each Django app, and they are Python files named urls.py.
#A URLconf maps URL patterns to views. To get from a URL to a view, Django uses what are known as ‘URLconfs’. A URLconf maps URL patterns to views

# Create your views here.

#The render() function takes the request object as its first argument, 
#a template name as its second argument and a dictionary as its optional third argument. It returns an HttpResponse object of the given template rendered with the given context.
# def index(request):
#     latest_question_list = Question.objects.order_by("-pub_date")[:5]
#     context = {"latest_question_list": latest_question_list}
#     return render(request, "myapp/index.html", context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, "myapp/detail.html", {"question": question})


# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)


# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)

####

#view to load question and choices then submits the choice through POST
def quiz_view(request, question_id=None):
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid.uuid4())  
    session_id = request.session['session_id']
    # print(f"session_id= {session_id}")
    
    #question_id comes from URL or is None if first question
    if question_id is None:
        question = Quiz_Question.objects.first()  #start with the first question
    else:
        question = get_object_or_404(Quiz_Question, pk=question_id)

    if not question:
        return render(request, 'myapp/quiz_thanks.html')  #no more questions

    return render(request, 'myapp/quiz.html', {'question': question, 'session_id' : session_id})

#view for django to retrieve the choice that was submitted, saves then redirects to thanks page
#not actually rendering any html - only two webpages exist
def quiz_submit(request):
    #  selected_choice = question.choice_set.get(pk=request.POST["choice"])
    if request.method == "POST":
        choice_id = request.POST.get("choice_id") 
        question_id = request.POST.get('question_id')
        session_id = request.POST.get('session_id')

        print(f"Received: choice_id={choice_id}, question_id={question_id}, session_id={session_id}")  #debugging in terminal output
        
        #save to Quiz_User model
        selected_question = get_object_or_404(Quiz_Question, pk=question_id)
        selected_choice = get_object_or_404(Quiz_Choice, pk=choice_id)
        user = Quiz_Response(session_id=session_id, question=selected_question, choice=selected_choice)
        user.save() #TODO update for not saving same session_id (if user hits back button??)
        
        next_question = None ##TODO CHANGE THIS
        if next_question:
            return redirect('myapp:quiz', question_id=next_question.id)  
        else:
            return HttpResponseRedirect(reverse('myapp:quiz_thanks')) 
     
    #HttpResponseRedirect takes a single argument: the URL to which the user will be redirected. should always be used with POST
    #reverse() returns the URL from the URL name specified
    return HttpResponseRedirect(reverse('myapp:quiz'))

def quiz_thanks(request):
    return render(request, "myapp/quiz_thanks.html")

