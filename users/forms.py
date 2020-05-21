from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Activity


class DateInput(forms.DateInput):
	input_type = 'date'

class CreateParticipant(forms.Form):
	age_groups = [('5 and below', '5 and below'), ('6-8','6-8'), ('9-11','9-11'), ('18+','18+')]
	first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'placeholder':'Please enter the participants first name.', 'size': 33}))
	age_group = forms.ChoiceField(choices=age_groups)


class EditActivity(forms.ModelForm):
	date = forms.DateField(widget=DateInput(attrs={'placeholder':'Enter as month/day/year - 01/01/20', 'size': 33}))
	miles = forms.DecimalField(max_digits=3, decimal_places=1, label='Miles/Number', help_text='Enter miles for Biking/Walking/Running, or number for Sit-ups/Push-ups')
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
		return data

class CreateActivity(forms.Form):
	activity_choices = [('Biking','Biking'), ('Walking', 'Walking'), ('Running','Running'), ('Push-ups','Push-ups'), ('Sit-ups','Sit-ups'), ('Wall-sits','Wall-sits' )]
	activity_type = forms.ChoiceField(choices=activity_choices)
	date = forms.DateField(widget=DateInput(attrs={'placeholder':'Enter as month/day/year - 01/01/20', 'size': 33, 'type': 'date'}))
	miles = forms.DecimalField(max_digits=3, decimal_places=1, label='Miles/Number', help_text='Enter miles for Biking/Walking/Running, or number for Sit-ups/Push-ups')
	time = forms.DurationField(help_text='Enter your time as hours:minutes:seconds - 00:45:20', label='Time Spent')

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )
