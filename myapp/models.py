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

class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    #Django creates a set (defined as "choice_set") to hold the "other side" of a ForeignKey
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

###

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
    session_id = models.CharField(max_length=36, editable=False)
    question = models.ForeignKey(Quiz_Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Quiz_Choice, on_delete=models.CASCADE)

    def __str__(self):
        return self.session_id
