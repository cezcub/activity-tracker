from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CreateParticipant, CreateActivity, SignUpForm
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
def create_activity(request, str):
	my_form = CreateActivity()
	if request.method == 'POST':
		my_form = CreateActivity(request.POST)
		if my_form.is_valid():
			my_dict = my_form.cleaned_data
			participants = Participant.objects.filter(first_name=str, admin=request.user)
			my_dict.update({'user': participants[0]})
			Activity.objects.create(**my_dict)
			return redirect('/home/')
	return render(request, 'activity.html', {'form': my_form})