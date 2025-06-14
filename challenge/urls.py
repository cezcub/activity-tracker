"""challenge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from pages.views import home_view, index_view, progress_view, superuser_profile, awards_view
from users.views import (create_user, create_participant, create_activity, delete_participant,
	edit_activity, delete_activity, superuser_activity, superuser_participant)

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', index_view, name='index'),
	path('progress/', progress_view, name='progress'),
	path('accounts/', include('django.contrib.auth.urls')),
	path('home/', home_view, name='home'),
	path('create_user/', create_user, name='sign-up'),
	path('create_participant/', create_participant, name='create-person'),
	path('create_activity/<str:str>', create_activity, name='new-activity'),
	path('delete_participant/<str:str>', delete_participant, name='delete-participant'),
	path('edit_activity/<int:pk>', edit_activity, name='edit-activity'),
	path('delete_activity/<int:pk>', delete_activity, name='delete-activity'),
	path('home/<str:name>', superuser_profile, name='superuser_profile'),
	path('create_activity/<str:str>/<str:name>', superuser_activity, name='superuser_activity'),
	path('create_participant/<str:name>', superuser_participant, name='superuser_participant'),
]
