from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Participant, Activity
from django.db.models import Avg, Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast

# Create your views here.
def index_view(request, *args, **kwargs):
	context = {}
	return render(request, 'index.html', context)

@login_required
def home_view(request):
	participants2 = {}
	participants = Participant.objects.filter(admin=request.user)
	for i in range(len(participants)):
		activities = []
		activity = Activity.objects.filter(user=participants[i])
		activities.append(Activity.objects.filter(user=participants[i]))
		participants2.update({i: {"ParticipantDetails": participants[i], "ParticipantActivities": activities}})
	context={
		'participants': participants2,
	}
	return render(request, 'home.html', context)

@login_required
def progress_view(request):
	d = {}
	participants = Participant.objects.order_by('age_group', 'first_name')
	for i in participants:
		activities = []
		activities.append(Activity.objects.filter(user=i, activity_type='Push-ups').aggregate(push_average=Cast(Avg('miles'), IntegerField())))
		activities.append(Activity.objects.filter(user=i, activity_type='Sit-ups').aggregate(sit_average=Cast(Avg('miles'), IntegerField())))
		activities.append(Activity.objects.filter(user=i, activity_type__contains='ing').aggregate(total_miles=Sum('miles')))
		d.update({i: activities})
		context = {
			"dict": d
		}
	return render(request, 'progress.html', context)