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
import json

# Create your views here.
def index_view(request, *args, **kwargs):
	context = {
		'date': abs(datetime.now(timezone(timedelta(hours=-5))).date().day - date(2020, 6, 30).day),
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
		participants2 = {}
		participants = Participant.objects.filter(admin=request.user)
		page_number = request.GET.get('page')
		for i in participants:
			activity = Activity.objects.filter(user=i).order_by('-date')
			paginator = Paginator(activity, 10)
			page = paginator.get_page(page_number)
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
			'current_page': page_number,
			'form': my_form,
			'date': abs(datetime.now(timezone(timedelta(hours=-5))).date().day - date(2020, 6, 30).day),
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
		participants2 = {}
		participants = Participant.objects.filter(admin=profile)
		page_number = request.GET.get('page')
		for i in participants:
			activity = Activity.objects.filter(user=i).order_by('-date')
			paginator = Paginator(activity, 10)
			page = paginator.get_page(page_number)
			participants2.update({i: page})
		context={
			'participants': participants2,
			'current_page': page_number,
			'username': name
		}
		return render(request, 'home-superuser.html', context)

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
	participants = Participant.objects.all()
	order_by = request.GET.get('order_by', 'total_miles')
	if order_by not in ['total_miles', 'sit_average', 'push_average', '-total_miles', '-sit_average', '-push_average']:
		participants = Participant.objects.order_by(order_by)
	doubles = []
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
			if activities['progress'] >= 200:
				activities.update({'double': True, 'complete': True})
			elif activities['progress'] >= 100:
				activities.update({'complete': True})
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
			if activities['progress'] >= 100:
				activities.update({'complete': True})
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
			if activities['progress'] >= 100:
				activities.update({'complete': True})
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
			if activities['progress'] >= 100:
				activities.update({'complete': True})
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
	queryset1 = Participant.objects.filter(activity__activity_type='Running').annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:5]
	queryset2 = Participant.objects.filter(activity__activity_type='Running').annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[5:]
	context = {
		"dict": d,
		"dict2": d2,
		"dict3": d3,
		"dict4": d4,
		"5_runners": queryset1,
		"other_runners": queryset2,
		"url": order_by,
		"date": abs(datetime.now(timezone(timedelta(hours=-5))).date().day - date(2020, 6, 30).day),
	}
	if request.GET.get("full_leaderboard") == "True":
		context.update({"full_leaderboard": True})
	return render(request, 'progress.html', context)

@login_required
def awards_view(request):
	context = {
		"adult_miles": Participant.objects.filter(age_group="18+", activity__activity_type__in=["Running", "Walking", "Biking"]).annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by("-total_miles")[:1],
		"adult_running_miles": Participant.objects.filter(activity__activity_type='Running', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"adult_walking_miles": Participant.objects.filter(activity__activity_type='Walking', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"adult_biking_miles": Participant.objects.filter(activity__activity_type='Biking', age_group="18+").annotate(total_miles=Cast(Sum('activity__miles')*2, IntegerField())).order_by('-total_miles')[:1],
		"adult_longest_run": Participant.objects.filter(activity__activity_type='Running', age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"adult_longest_walk": Participant.objects.filter(activity__activity_type='Walking', age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"adult_longest_bike": Participant.objects.filter(activity__activity_type='Biking', age_group="18+").annotate(most_miles=Cast(Max("activity__miles")*2, IntegerField())).order_by("-most_miles")[:1],
		"adult_best_push": Participant.objects.filter(activity__activity_type='Push-ups', age_group="18+").annotate(push_average=Cast(Avg('activity__miles'), IntegerField())).order_by("-push_average")[:1],
		"adult_best_sit": Participant.objects.filter(activity__activity_type='Sit-ups', age_group="18+").annotate(sit_average=Cast(Avg('activity__miles'), IntegerField())).order_by("-sit_average")[:1],
		"child_miles": Participant.objects.exclude(age_group="18+", activity__activity_type__in=["Sit-ups", "Push-ups", "Wall-sits"]).annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by("-total_miles")[:1],
		"child_running_miles": Participant.objects.filter(activity__activity_type='Running').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"child_walking_miles": Participant.objects.filter(activity__activity_type='Walking').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles'), IntegerField())).order_by('-total_miles')[:1],
		"child_biking_miles": Participant.objects.filter(activity__activity_type='Biking').exclude(age_group="18+").annotate(total_miles=Cast(Sum('activity__miles')*2, IntegerField())).order_by('-total_miles')[:1],
		"child_longest_run": Participant.objects.filter(activity__activity_type='Running').exclude(age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"child_longest_walk": Participant.objects.filter(activity__activity_type="Walking").exclude(age_group="18+").annotate(most_miles=Max("activity__miles")).order_by("-most_miles")[:1],
		"child_longest_bike": Participant.objects.filter(activity__activity_type='Biking').exclude(age_group="18+").annotate(most_miles=Cast(Max("activity__miles")*2, IntegerField())).order_by("-most_miles")[:1],
		"child_best_push": Participant.objects.filter(activity__activity_type='Push-ups').exclude(age_group="18+").annotate(push_average=Cast(Avg('activity__miles'), IntegerField())).order_by("-push_average")[:1],
		"child_best_sit": Participant.objects.filter(activity__activity_type='Sit-ups').exclude(age_group="18+").annotate(sit_average=Cast(Avg('activity__miles'), IntegerField())).order_by("-sit_average")[:1],
	}
	return render(request, 'awards.html', context)


