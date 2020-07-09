from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import Participant, Activity
from django.db.models import Avg, Sum, Max
from django.db.models import IntegerField
from django.db.models.functions import Cast
from collections import OrderedDict 
from operator import getitem
from django.core.paginator import Paginator
from datetime import date, timedelta, datetime, timezone
from django.contrib.auth.models import User
from django.http import Http404
from .forms import TriviaForm
from .models import Trivia
from decimal import Decimal

# Create your views here.
def index_view(request, *args, **kwargs):
	daily_activities = dict(zip([x for x in reversed(range(1, 33))], ['Sit-ups', 'Squats', 'Push-ups', 'Plank', 'Jumping jacks', 'Leg lifts', 'Lunges', 'Burpees']*4))
	context = {
		'date': abs((datetime.now(timezone(timedelta(hours=-5))).date() - date(2020, 8, 7)).days),
		'activity': daily_activities[abs((datetime.now(timezone(timedelta(hours=-5))).date() - date(2020, 8, 8)).days)],
	}
	return render(request, 'index.html', context)

@login_required
def home_view(request):
	if request.user.is_superuser:
		queryset = User.objects.all()
		context = {
			'objects': queryset
		}
		return render(request, 'list.html', context)
	else:
		daily_activities = dict(zip([x for x in reversed(range(1, 33))], ['Sit-ups', 'Squats', 'Push-ups', 'Plank', 'Jumping jacks', 'Leg lifts', 'Lunges', 'Burpees']*4))
		participants2 = {}
		run_swim_goal = {}
		participants = Participant.objects.filter(admin=request.user)
		page_number = request.GET.get('page')
		for i in participants:
			activity = Activity.objects.filter(user=i).order_by('-date')
			paginator = Paginator(activity, 10)
			page = paginator.get_page(page_number)
			running = Activity.objects.filter(user=i, activity_type="Running").aggregate(running_miles=Sum('miles')/Decimal(1.5))
			swimming = Activity.objects.filter(user=i, activity_type="Swimming").aggregate(swimming_miles=Sum('miles')/Decimal(2.5))
			if running['running_miles'] == None:
				running['running_miles'] = 0
			if swimming['swimming_miles'] == None:
				swimming['swimming_miles'] = 0
			run_swim = round(running['running_miles'] + swimming['swimming_miles'], 1)
			run_swim_goal.update({i: run_swim})
			participants2.update({i: page})
		queryset = Trivia.objects.filter(date=datetime.now(timezone(timedelta(hours=-5))).date())
		answered = []
		for i in queryset:
			answered.append(i.user)
		my_form = TriviaForm()
		if request.method == "POST" and request.user not in answered:
			my_form = TriviaForm(request.POST)
			if my_form.is_valid():
				my_dict = my_form.cleaned_data
				my_dict.update({"date": datetime.now(timezone(timedelta(hours=-5))).date(), "user": request.user})
				Trivia.objects.create(**my_dict)
				return redirect('/home/?page=1')
		context={

			'participants': participants2,
			'special_goal': run_swim_goal,
			'current_page': page_number,
			'activity': daily_activities[abs((datetime.now(timezone(timedelta(hours=-5))).date() - date(2020, 8, 8)).days)],
			'form': my_form,
			'date': abs((datetime.now(timezone(timedelta(hours=-5))).date() - date(2020, 8, 6)).days),
		}
		if request.user in answered:
			context.update({"answered": True})
		yesterdays_answers = Trivia.objects.filter(date=(datetime.now(timezone(timedelta(hours=-5))).date() - timedelta(days=1)))
		for i in yesterdays_answers:
			if request.user == i.user:
				if i.answer.lower() == "teapot":
					context.update({"correct": True})
				break
		else:
			context.update({"correct": "unanswered"})
			return render(request, 'home.html', context)

@login_required
def superuser_profile(request, name):
	if not request.user.is_superuser:
		raise Http404
	else:
		profile = User.objects.get(username=name)
		run_swim_goal = {}
		participants2 = {}
		participants = Participant.objects.filter(admin=profile)
		page_number = request.GET.get('page')
		for i in participants:
			activity = Activity.objects.filter(user=i).order_by('-date')
			paginator = Paginator(activity, 10)
			page = paginator.get_page(page_number)
			running = Activity.objects.filter(user=i, activity_type="Running").aggregate(running_miles=Sum('miles')/Decimal(1.5))
			swimming = Activity.objects.filter(user=i, activity_type="Swimming").aggregate(swimming_miles=Sum('miles')/Decimal(2.5))
			if running['running_miles'] == None:
				running['running_miles'] = 0
			if swimming['swimming_miles'] == None:
				swimming['swimming_miles'] = 0
			run_swim = round(running['running_miles'] + swimming['swimming_miles'], 1)
			run_swim_goal.update({i: run_swim})
			participants2.update({i: page})
		context={
			'participants': participants2,
			'special_goal': run_swim_goal,
			'current_page': page_number,
			'username': name,
		}
		return render(request, 'home-superuser.html', context)

@login_required
def progress_view(request):
	start_date = date(2020, 7, 6)
	end_date = date(2020, 8, 7)
	current_date = date.today()
	date_diff = current_date - start_date
	total_days = end_date - start_date
	percentage_days = round((date_diff.days/total_days.days)*100)
	d = {}
	d2 = {}
	d3 = {}
	d4 = {}
	participants = Participant.objects.all()
	order_by = request.GET.get('order_by', 'total_miles')
	if order_by not in ['total_miles', '-total_miles']:
		participants = Participant.objects.order_by(order_by)
	doubles = []
	for i in participants:
		activities = {}
		activities.update(Activity.objects.filter(user=i).aggregate(total_miles=Sum('miles')))
		running = Activity.objects.filter(user=i, activity_type="Running").aggregate(running_miles=Sum('miles')/1.5)
		swimming = Activity.objects.filter(user=i, activity_type="Swimming").aggregate(swimming_miles=Sum('miles')/2.5)
		activities.update(running)
		activities.update(swimming)
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
			if activities['progress'] >= 200:
				activities.update({'double': True, 'complete': True})
			elif activities['progress'] >= 100:
				activities.update({'complete': True})
			if activities['running_miles'] + activities['swimming_miles'] >= 20:
				activities.update({'complete2': True})
			d.update({i: activities})
		elif i.age_group == '9-11':
			activities.update({'progress': round((activities['total_miles']/70)*100, 2)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			if activities['progress'] >= 200:
				activities.update({'double': True, 'complete': True})
			elif activities['progress'] >= 100:
				activities.update({'complete': True})
			if activities['running_miles'] + activities['swimming_miles'] >= 28:
				activities.update({'complete2': True})
			d2.update({i: activities})
		elif i.age_group == '6-8':
			activities.update({'progress': round(activities['total_miles']*2)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			if activities['progress'] >= 200:
				activities.update({'double': True, 'complete': True})
			elif activities['progress'] >= 100:
				activities.update({'complete': True})
			if activities['running_miles'] + activities['swimming_miles'] >= 15:
				activities.update({'complete2': True})
			d3.update({i: activities})
		elif i.age_group == '5 and below':
			activities.update({'progress': round((activities['total_miles']/30)*100)})
			if activities['progress'] - 20 >= percentage_days:
				activities.update({'class': 'flair'})
			elif activities['progress'] >= percentage_days:
				activities.update({'class': 'green'})
			elif activities['progress'] < percentage_days:
				activities.update({'class': 'red'})
			if activities['progress'] >= 200:
				activities.update({'double': True, 'complete': True})
			elif activities['progress'] >= 100:
				activities.update({'complete': True})
			if activities['running_miles'] + activities['swimming_miles'] >= 5:
				activities.update({'complete2': True})
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
	context = {
		"dict": d,
		"dict2": d2,
		"dict3": d3,
		"dict4": d4,
		"url": order_by,
		"date": abs((datetime.now(timezone(timedelta(hours=-5))).date() - date(2020, 8, 6)).days),
	}
	if request.GET.get("full_leaderboard") == "True":
		context.update({"full_leaderboard": True})
	return render(request, 'progress.html', context)

@login_required
def awards_view(request):
	context = {
		"adult_miles": Participant.objects.filter(age_group="18+", activity__activity_type__in=["Running", "Walking", "Biking", "Swimming"]).annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by("-total_miles")[:1],
		"adult_running_miles": Participant.objects.filter(activity__activity_type='Running', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"adult_walking_miles": Participant.objects.filter(activity__activity_type='Walking', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"adult_biking_miles": Participant.objects.filter(activity__activity_type='Biking', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles')*2, IntegerField())).order_by('-total_miles')[:1],
		"adult_longest_run": Participant.objects.filter(activity__activity_type='Running', age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"adult_longest_walk": Participant.objects.filter(activity__activity_type='Walking', age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"adult_longest_bike": Participant.objects.filter(activity__activity_type='Biking', age_group="18+").annotate(most_miles=Cast(Max("activity__miles")*2, IntegerField())).order_by("-most_miles")[:1],
		"child_miles": Participant.objects.exclude(age_group="18+").filter().annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by("-total_miles")[:1],
		"child_running_miles": Participant.objects.filter(activity__activity_type='Running').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"child_walking_miles": Participant.objects.filter(activity__activity_type='Walking').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"child_biking_miles": Participant.objects.filter(activity__activity_type='Biking').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles')*2, IntegerField())).order_by('-total_miles')[:1],
		"child_longest_run": Participant.objects.filter(activity__activity_type='Running').exclude(age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"child_longest_walk": Participant.objects.filter(activity__activity_type="Walking").exclude(age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"child_longest_bike": Participant.objects.filter(activity__activity_type='Biking').exclude(age_group="18+").annotate(most_miles=Cast(Max("activity__miles")*2, IntegerField())).order_by("-most_miles")[:1],
	}
	return render(request, 'awards.html', context)