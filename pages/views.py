from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import Participant, Activity
from django.db.models import Avg, Sum
from django.db.models import IntegerField
from django.db.models.functions import Cast
from collections import OrderedDict 
from operator import getitem
from datetime import date

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
	start_date = date(2020, 5, 15)
	end_date = date(2020, 6, 30)
	current_date = date.today()
	date_diff = current_date - start_date
	total_days = end_date - start_date
	percentage_days = round((date_diff.days/total_days.days)*100)
	d = {}
	d2 = {}
	d3 = {}
	d4 = {}
	participants = Participant.objects.order_by('first_name')
	order_by = request.GET.get('order_by', 'first_name')
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
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			d.update({i: activities})
		elif i.age_group == '9-11':
			activities.update({'progress': round((activities['total_miles']/70)*100, 2)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			d2.update({i: activities})
		elif i.age_group == '6-8':
			activities.update({'progress': round(activities['total_miles']*2)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			d3.update({i: activities})
		elif i.age_group == '5 and below':
			activities.update({'progress': round((activities['total_miles']/30)*100)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			d4.update({i: activities})
	if order_by == 'total_miles':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'total_miles'), reverse=True))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'total_miles'), reverse=True))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'total_miles'), reverse=True))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'total_miles'), reverse=True))
	elif order_by == '-total_miles':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'total_miles')))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'total_miles')))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'total_miles')))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'total_miles')))
	elif order_by == 'push_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'push_average'), reverse=True))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'push_average'), reverse=True))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'push_average'), reverse=True))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'push_average'), reverse=True))
	elif order_by == '-push_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'push_average')))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'push_average')))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'push_average')))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'push_average')))
	elif order_by == 'sit_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'sit_average'), reverse=True))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'sit_average'), reverse=True))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'sit_average'), reverse=True))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'sit_average'), reverse=True))
	elif order_by == '-sit_average':
		d = OrderedDict(sorted(d.items(), key = lambda x: getitem(x[1], 'sit_average')))
		d2 = OrderedDict(sorted(d2.items(), key = lambda x: getitem(x[1], 'sit_average')))
		d3 = OrderedDict(sorted(d3.items(), key = lambda x: getitem(x[1], 'sit_average')))
		d4 = OrderedDict(sorted(d4.items(), key = lambda x: getitem(x[1], 'sit_average')))
	context = {
		"dict": d,
		"dict2": d2,
		"dict3": d3,
		"dict4": d4,
		"progress": [start_date, end_date, date_diff, current_date, percentage_days, total_days]
	}
	return render(request, 'progress.html', context)