from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
import uuid

from django.db.models import F
from django.urls import reverse

from .models import Quiz_Question, Quiz_Choice, Quiz_User, Quiz_Response
from myapp.scripts.cluster_input import ClusteringModelManager
import myapp.scripts.results_page as rp

from django.http import FileResponse
import os
import tempfile

#A view is a “type” of web page in your Django application that generally serves a specific function and has a specific template
#views return HttpResponse
#In Django, web pages and other content are delivered by views. Each view is represented by a Python function (or method, in the case of class-based views). 
#Django will choose a view by examining the URL that’s requested (to be precise, the part of the URL after the domain name).

#to access view in a browser, we need to map it to a URL - and for this we need to define a URL configuration, 
#or “URLconf” for short. These URL configurations are defined inside each Django app, and they are Python files named urls.py.
#A URLconf maps URL patterns to views. To get from a URL to a view, Django uses what are known as ‘URLconfs’. A URLconf maps URL patterns to views

#The render() function takes the request object as its first argument, 
#a template name as its second argument and a dictionary as its optional third argument. It returns an HttpResponse object of the given template rendered with the given context.

#view to load question and choices then submits the choice through POST
def quiz_view(request, question_id=None):
    # if request.session.get('session_id') == None:
    #generate own sessionid and instead of having users type in login info
    if 'session_id' not in request.session:
        request.session['session_id'] = str(uuid.uuid4())  
    session_id = request.session['session_id']
    # print(f"session_id= {session_id}")
    
    #question_id comes from URL or is None if first question
    if question_id is None:
        question = Quiz_Question.objects.get(order=1)  #start with the first question
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

        # print(f"Received: choice_id={choice_id}, question_id={question_id}, session_id={session_id}")  #debugging in terminal output
        
        #save to models
        user, created = Quiz_User.objects.get_or_create(session_id=session_id)
        if created:
            user.save()
        
        else:
            user = Quiz_User.objects.get(session_id=session_id)
        
        # print(f"User: {user.session_id}; Exists: {Quiz_User.objects.filter(session_id=session_id).exists()}; PK: {user.pk}")
        
        selected_question = get_object_or_404(Quiz_Question, pk=question_id)
        selected_choice = get_object_or_404(Quiz_Choice, pk=choice_id)
        
        # print(f"Saving Response with user: {user}, question: {selected_question}, choice: {selected_choice}")
        answers_set = Quiz_Response.objects.filter(session_id=user, question=selected_question)
        if answers_set.exists(): 
            answers_set.delete()
            response, created = Quiz_Response.objects.get_or_create(session_id=user, question=selected_question, choice=selected_choice)
            response.save()

        else:
            response, created = Quiz_Response.objects.get_or_create(session_id=user, question=selected_question, choice=selected_choice)
            response.save()
        
        #id__gt is id greater than
        current_order = getattr(selected_question, 'order')
        next_question =  Quiz_Question.objects.filter(order=current_order+1).first() #next question logic
        if next_question:
            #use redirect() it's simpler takes more options
            return redirect('myapp:quiz', question_id=next_question.id)  
        else:
            #HttpResponseRedirect only takes the URL to which the user will be redirected. should always be used with POST; changes URL/view
            #reverse() returns the URL from the URL name specified
            return HttpResponseRedirect(reverse('myapp:quiz_thanks')) 
     
    return HttpResponseRedirect(reverse('myapp:quiz_index'))   


def quiz_thanks(request, session_id=None):   
    session_id = request.session['session_id']

    my_cluster = ClusteringModelManager()
    user_cluster = my_cluster.get_user_cluster(session_id=session_id)

    user_percentile, user_grade = rp.generate_percentile_grade(session_id=session_id)
    rp.generate_similar_subgroup(session_id=session_id)
    rp.generate_user_categories(session_id=session_id)
    recs = rp.recommended_actions(session_id=session_id)

    return render(request, "myapp/quiz_thanks.html", {
        'user_percentile': user_percentile, 
        'user_grade': user_grade, 
        'recs': recs, 
        'user_cluster': user_cluster})


def ML_view(request):
    return render(request, "myapp/ML.html")


def about_view(request):
    return render(request, "myapp/about.html")
 

def serve_chart(request, filename):
    allowed = ['percentile.png', 'subgroups.png', 'top5.png']
    
    if filename not in allowed:
        return HttpResponseNotFound()

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    return FileResponse(open(tmp_path, 'rb'), content_type='image/png')