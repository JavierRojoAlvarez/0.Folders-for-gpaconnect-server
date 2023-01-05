from django.urls import path
from accounting.views import StatementsTemplateView


urlpatterns = [
	path('statements/', StatementsTemplateView.as_view(), name = 'statements'),
]
