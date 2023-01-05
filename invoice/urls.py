from django.urls import path
from invoice.views import *


urlpatterns = [
	path('preview/', preview_pdf, name = 'preview'),
	path('create/<int:pk>/', ReceivedInvoiceCreateView.as_view(),
		name = 'invoice-create'),
]
