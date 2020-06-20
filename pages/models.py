from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Trivia(models.Model):
	answer = models.CharField(max_length=100)
	date = models.DateField()
	user = models.ForeignKey(User, on_delete=models.CASCADE)