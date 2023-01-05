from django.urls import path
from api.views import *


urlpatterns = [
	path('line/', TrackerAPI.as_view(), name = 'tracker'),
	path('cheese/', CheeseAPI.as_view(), name = 'cheese-api'),
	path('liability/', Liability.as_view(), name = 'liability-api'),
]
