from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Participant, Activity

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
		print(activities)
		participants2.update({i: {"ParticipantDetails": participants[i], "ParticipantActivities": activities}})
	context={
		'participants': participants2,
	}
	return render(request, 'home.html', context)

@login_required
def progress_view(request):
	participants2 = {}
	participants = Participant.objects.all()
	for i in range(len(participants)):
		activities = []
		activities.append(Activity.objects.filter(user=participants[i]))
		participants2.update({i: {"ParticipantDetails": participants[i], "ParticipantActivities": activities}})
	context={
		'participants': participants2,
	}
	return render(request, 'progress.html', context)