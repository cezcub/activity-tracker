from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Participant, Activity
from django.db.models import Avg, Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast
from collections import OrderedDict 
from operator import getitem
from functools import reduce

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
	d2 = {}
	d3 = {}
	d4 = {}
	d5 = {}
	participants = Participant.objects.order_by('first_name')
	order_by = request.GET.get('order_by', 'first_name')
	order_group = request.GET.get('group', '18+')
	if order_by not in ['total_miles', 'sit_average', 'push_average', '-total_miles', '-sit_average', '-push_average']:
		participants = Participant.objects.order_by(order_by)
	for i in participants:
		activities = {}
		activities.update(Activity.objects.filter(user=i, activity_type='Push-ups').aggregate(push_average=Cast(Avg('miles'), IntegerField())))
		activities.update(Activity.objects.filter(user=i, activity_type='Sit-ups').aggregate(sit_average=Cast(Avg('miles'), IntegerField())))
		activities.update(Activity.objects.filter(user=i, activity_type__contains='ing').aggregate(total_miles=Sum('miles')))
		for key, value in activities.items():
			if value == None:
				activities[key] = 0
		if i.age_group == '18+':
			activities.update({'progress': round(activities['total_miles'], 2)})
			d5.update({i: activities})
		elif i.age_group == '9-11':
			activities.update({'progress': round((activities['total_miles']/70)*100, 2)})
			d2.update({i: activities})
		elif i.age_group == '6-8':
			activities.update({'progress': round(activities['total_miles']*2, 2)})
			d3.update({i: activities})
		elif i.age_group == '5 and below':
			activities.update({'progress': round((activities['total_miles']/30)*100, 2)})
			d4.update({i: activities})
	
	if d5:
		d.update({'18+': d5})
	if d2:
		d.update({'9-11': d2})
	if d3:
		d.update({"6-8": d3})
	if d4:
		d.update({"5 and below": d4})
	
	if order_by == 'total_miles':
		d = OrderedDict(sorted(d.items(), key = lambda x: reduce(lambda val, key: val.get(key) if val else 0, ['total_miles'], x[1]), reverse=True))
	elif order_by == '-total_miles':
		d = OrderedDict(sorted(d.items(), key = lambda x: reduce(lambda val, key: print(val.get(key)) if val else 0, ['total_miles'], x)))
	elif order_by == 'push_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1][1], 'push_average'), reverse=True))
	elif order_by == '-push_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1][1], 'push_average')))
	elif order_by == 'sit_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'sit_average'), reverse=True))
	elif order_by == '-sit_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'sit_average')))
	context = {
		"dict": d,
	}
	return render(request, 'progress.html', context)