from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Participant(models.Model):
	age_groups = [('below 5', 'below 5'), ('5-8','5-8'), ('9-10','9-10'), ('11-18','11-18'), ('18+','18+')]
	first_name = models.CharField(max_length=50)
	age_group = models.CharField(max_length=10, choices=age_groups)
	admin = models.ForeignKey(User, on_delete=models.CASCADE)

class Activity(models.Model):
	activity_choices = [('Biking','Biking'), ('Walking', 'Walking'), ('Running','Running')]
	activity_type = models.CharField(max_length=7, choices=activity_choices)
	date = models.DateField()
	user = models.ForeignKey(Participant, on_delete=models.CASCADE)
	miles = models.DecimalField(max_digits=2, decimal_places=1)