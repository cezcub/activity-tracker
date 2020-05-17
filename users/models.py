from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Participant(models.Model):
	age_groups = [('5 and below', '5 and below'), ('6-8','6-8'), ('9-11','9-11'), ('18+','18+')]
	first_name = models.CharField(max_length=50)
	age_group = models.CharField(max_length=10, choices=age_groups)
	admin = models.ForeignKey(User, on_delete=models.CASCADE)

class Activity(models.Model):
	activity_choices = [('Biking','Biking'), ('Walking', 'Walking'), ('Running','Running'), ('Push-ups','Push-ups'), ('Sit-ups','Sit-ups')]
	activity_type = models.CharField(max_length=10, choices=activity_choices)
	date = models.DateField()
	user = models.ForeignKey(Participant, on_delete=models.CASCADE)
	miles = models.DecimalField(max_digits=3, decimal_places=1)