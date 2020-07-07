from django.core.exceptions import ValidationError
from datetime import datetime, date, timedelta, timezone

def date_checker(value):
	if value > date(2020, 8, 7) or value < date(2020, 7, 6):
		raise ValidationError("%(value)s is not a valid date",
		params={'value': value},
		)
	return value