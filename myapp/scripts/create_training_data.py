from myapp.models import Quiz_Response, Quiz_Choice, Quiz_Question, Quiz_User
import uuid
import random

## from myapp.scripts.create_training_data import create_data

weighted_choices = {
        'beef': [0.2, 0.3, 0.4, 0.1],
        'lamb': [0.2, 0.1, 0.1, 0.6],
        'oth_meat': [0.2, 0.3, 0.4, 0.1],
        'car_type': [0.2, 0.2, 0.2, 0.1, 0.05, 0.02, 0.13, 0.1],
        'miles_driven': [0.1, 0.3, 0.4, 0.1, 0.1],
        'flights': [0.4, 0.15, 0.1, 0.05, 0.3],
        'home_electricity': [0.2, 0.8],
        'shopping': [0.3, 0.2, 0.2, 0.2, 0.1]
    }

def create_data(n=1):
    for _ in range(n):
        user_id = uuid.uuid4()
        for question in Quiz_Question.objects.all():
            question_short = question.question_short
            choices = question.quiz_choice_set.all()
            chosen_choice = random.choices(choices,weights=weighted_choices.get(question_short))

            user, created = Quiz_User.objects.get_or_create(session_id=user_id)
            if created:
                user.save()
            response = Quiz_Response(session_id=user, question=question, choice=chosen_choice[0])
            response.save() 


