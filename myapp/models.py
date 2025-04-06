from django.db import models

# Create your models (data tables) here.

#Here, each model is represented by a class that subclasses django.db.models.Model. Each model has a number of class variables, each of which represents a database field in the model.
#Each field is represented by an instance of a Field class

#remember the three-step guide to making model changes:
    # Change your models (in models.py).
    # Run python manage.py makemigrations to create migrations for those changes
    # Run python manage.py migrate to apply those changes to the database.

    #python manage.py shell
    #from myapp.models import Quiz_User
    #Quiz_User.objects.all()

class Quiz_Question(models.Model):
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Quiz_Choice(models.Model):
    #Django creates a set (defined as "quiz_choice_set") to hold the "other side" of a ForeignKey
    question = models.ForeignKey(Quiz_Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text
    
class Quiz_User(models.Model):
    session_id = models.CharField(primary_key=True, max_length=100, editable=False)

    def __str__(self):
        return self.session_id

class Quiz_Response(models.Model):
    # session_id = models.ForeignKey(Quiz_User, on_delete=models.CASCADE) #CHANGE THIS back to ForeignKey when not using SQLite
    session_id = models.CharField(max_length=100)
    question = models.ForeignKey(Quiz_Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Quiz_Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f" Choice: {self.choice.choice_text}"
