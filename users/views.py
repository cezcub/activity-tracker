from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, models
from .forms import CreateParticipant, CreateActivity, SignUpForm, EditActivity
from django.contrib.auth.decorators import login_required
from .models import Participant, Activity
from django.http import Http404
from decimal import Decimal

# Create your views here.
def create_user(request):
	if request.method == 'POST':
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			raw_password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=raw_password)
			login(request, user)
			return redirect('/home/?page=1')
	else:
		form = SignUpForm()
	return render(request, 'signup.html', {'form': form})

@login_required
def create_participant(request):
	my_form = CreateParticipant()
	if request.method == 'POST':
		my_form = CreateParticipant(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			my_dict.update({'admin': request.user})
			Participant.objects.create(**my_dict)
			return redirect('/home/?page=1')
	return render(request, 'formt.html', {'form': my_form})

@login_required
def edit_activity(request, pk):
	if request.user.is_superuser:
		participants = Participant.objects.all()
	else:
		participants = Participant.objects.filter(admin=request.user)
	activity = get_object_or_404(Activity, user__in=participants, id=pk)
	if activity.activity_type == 'Biking':
		my_form = EditActivity(request.POST or None, instance=activity, initial={'miles': activity.miles*2})
	elif activity.activity_type in ["Running", "Elliptical"]:
		my_form = EditActivity(request.POST or None, instance=activity, initial={'miles': activity.miles/Decimal(1.5)})
	elif activity.activity_type == "Swimming":
		my_form = EditActivity(request.POST or None, instance=activity, initial={'miles': activity.miles/Decimal(2.5)})
	else:
		my_form = EditActivity(request.POST or None, instance=activity)
	if my_form.is_valid():
		my_form.save(activity.user)
		return redirect('/home/?page=1')
	return render(request, 'form.html', {'form': my_form})

@login_required
def delete_activity(request, pk):
	if request.user.is_superuser:
		participants = Participant.objects.all()
	else:
		participants = Participant.objects.filter(admin=request.user)
	activity = get_object_or_404(Activity, user__in=participants, id=pk)
	if request.method == 'POST':
		activity.delete()
		return redirect('/home/?page=1')
	return render(request, 'delete_activity.html', {})

@login_required
def create_activity(request, str):
	my_form = CreateActivity()
	if request.method == 'POST':
		my_form = CreateActivity(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			participant = get_object_or_404(Participant, first_name=str, admin=request.user)
			my_dict.update({'user': participant})
			if my_dict['activity_type'] == "Biking":
				my_dict['miles'] = my_dict['miles']/2
			if my_dict['activity_type'] in ["Running", "Elliptical"]:
				my_dict['miles'] = my_dict['miles']*Decimal(1.5)
			if my_dict['activity_type'] == "Swimming":
				my_dict['miles'] = my_dict['miles']*Decimal(2.5)
			Activity.objects.create(**my_dict)
			return redirect('/home/?page=1')
	return render(request, 'form.html', {'form': my_form})

@login_required
def delete_participant(request, str):
	participant = get_object_or_404(Participant, first_name=str, admin=request.user)
	if request.method == 'POST':
		participant.delete()
		return redirect('/home/?page=1')
	return render(request, 'delete_participant.html', {})

@login_required
def superuser_activity(request, str, name):
	if not request.user.is_superuser:
		raise Http404
	my_form = CreateActivity()
	if request.method == 'POST':
		my_form = CreateActivity(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			user = models.User.objects.get(username=name)
			participant = get_object_or_404(Participant, first_name=str, admin=user)
			my_dict.update({'user': participant})
			if my_dict['activity_type'] == "Biking":
				my_dict['miles'] = my_dict['miles']/2
			if my_dict['activity_type'] in ["Running", "Elliptical"]:
				my_dict['miles'] = my_dict['miles']*Decimal(1.5)
			if my_dict['activity_type'] == "Swimming":
				my_dict['miles'] = my_dict['miles']*Decimal(2.5)
			Activity.objects.create(**my_dict)
			return redirect('/home/?page=1')
	return render(request, 'form.html', {'form': my_form})

@login_required
def superuser_participant(request, name):
	if not request.user.is_superuser:
		raise Http404
	user = models.User.objects.get(username=name)
	my_form = CreateParticipant()
	if request.method == 'POST':
		my_form = CreateParticipant(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			my_dict.update({'admin': user})
			Participant.objects.create(**my_dict)
			return redirect('/home/?page=1')
	return render(request, 'participant.html', {'form': my_form})
