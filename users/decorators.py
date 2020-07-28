import datetime
from functools import wraps
from django.utils import timezone

def confirm_password(view_func):
	@wraps(view_func)
	def _wrapped_view(request, *args, **kwargs):
		last_login = request.user.last_login
		timespan = last_login + datetime.timedelta(minutes=1)
		if timezone.now() > timespan:
			from .views import confirm_password_view
			return confirm_password_view(request)
		return view_func(request, *args, **kwargs)
	return _wrapped_view