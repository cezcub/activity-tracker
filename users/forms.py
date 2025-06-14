from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from .models import Activity
from decimal import Decimal
from django.core.exceptions import ValidationError
from .validators import date_checker
from django.utils import timezone

class DateInput(forms.DateInput):
	input_type = 'date'

class CreateParticipant(forms.Form):
	age_groups = [('5 and below', '5 and below'), ('6-8','6-8'), ('9-11','9-11'), ('18+','18+')]
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder':'Please enter the participants first name.', 'size': 33}))
	age_group = forms.ChoiceField(choices=age_groups)


class EditActivity(forms.ModelForm):
	date = forms.DateField(validators=[date_checker], widget=DateInput(attrs={'size': 33}))
	miles = forms.DecimalField(max_digits=3, decimal_places=1)
	class Meta:
		model = Activity
		fields = ['activity_type', 'date', 'miles', 'time']

	def save(self, user=None):
		activity = super(EditActivity, self).save(commit=False)
		if user:
			activity.user = user
		activity.save()
		return activity

	def clean_miles(self):
		data = self.cleaned_data['miles']
		if self.cleaned_data['activity_type'] == 'Biking':
			data = round(data/2, 1)
		elif self.cleaned_data['activity_type'] in ["Running", "Elliptical"]:
			myvar = Decimal(1.5)
			data = round(data*myvar, 1)
		elif self.cleaned_data['activity_type'] == "Swimming":
			myvar2 = Decimal(2.5)
			data = round(data*myvar2, 1)
		elif self.cleaned_data['activity_type'] == "Rowing":
			myvar3 = Decimal(1.2)
			data=round(data*myvar3, 1)
		return data

class CreateActivity(forms.Form):
	activity_choices = [('Biking','Biking'), ('Walking', 'Walking'), ('Running','Running'), ('Swimming', 'Swimming'), ('Elliptical', 'Elliptical'), ('Rowing', 'Rowing')]
	activity_type = forms.ChoiceField(choices=activity_choices)
	date = forms.DateField(validators=[date_checker], widget=DateInput(attrs={'size': 33}))
	miles = forms.DecimalField(max_digits=3, decimal_places=1)
	time = forms.DurationField(label='Time Spent')

class SignUpForm(UserCreationForm):
	email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2', )

class ConfirmPassword(forms.ModelForm):
	confirm_password = forms.CharField(widget=forms.PasswordInput())

	class Meta:
		model = User
		fields = ('confirm_password', )

	def clean(self):
		cleaned_data = super(ConfirmPassword, self).clean()
		confirm_password = cleaned_data.get('confirm_password')
		if not check_password(confirm_password, self.instance.password):
			self.add_error('confirm_password', 'Password does not match.')
	
	def save(self, commit=True):
		user = super(ConfirmPassword, self).save(commit)
		user.last_login = timezone.now()
		if commit:
			user.save()
		return user
