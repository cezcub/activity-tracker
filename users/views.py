from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import CreateParticipant, CreateActivity, SignUpForm, EditActivity
from django.contrib.auth.decorators import login_required
from .models import Participant, Activity

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
            return redirect('/home/')
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
			return redirect('/home/')
		else:
			return my_form.errors
	return render(request, 'participant.html', {'form': my_form})

@login_required
def edit_activity(request, pk):
	participants = Participant.objects.filter(admin=request.user)
	activity = get_object_or_404(Activity, user__in=participants, id=pk)
	if activity.activity_type == 'Biking':
		my_form = EditActivity(request.POST or None, instance=activity, initial={'miles': activity.miles*2})
	else:
		my_form = EditActivity(request.POST or None, instance=activity)
	if my_form.is_valid():
		my_form.save(activity.user)
		return redirect('/home/')
	return render(request, 'activity.html', {'form': my_form})

@login_required
def delete_activity(request, pk):
	participants = Participant.objects.filter(admin=request.user)
	activity = get_object_or_404(Activity, user__in=participants, id=pk)
	if request.method == 'POST':
		activity.delete()
		return redirect('/home/')
	return render(request, 'delete_activity.html', {})

@login_required
def create_activity(request, str):
	my_form = CreateActivity()
	if request.method == 'POST':
		my_form = CreateActivity(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			participants = Participant.objects.filter(first_name=str, admin=request.user)
			my_dict.update({'user': participants[0]})
			if my_dict['activity_type'] == "Biking":
				my_dict['miles'] = my_dict['miles']/2
			Activity.objects.create(**my_dict)
			return redirect('/home/')
	return render(request, 'activity.html', {'form': my_form})

@login_required
def delete_participant(request, str):
	participant = get_object_or_404(Participant, first_name=str, admin=request.user )
	if request.method == 'POST':
		participant.delete()
		return redirect('/home/')
	return render(request, 'delete_participant.html', {})
