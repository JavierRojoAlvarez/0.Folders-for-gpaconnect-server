from django import forms
from django.forms import ModelForm
from django.urls import reverse_lazy
from invoice.models import *
from website.settings import DATE_INPUT_FORMATS
from invoice.pdf import make_pdf_preview
from django.core.files.uploadedfile import *

reg_attrs = {'class':'form-control form-control-md rounded'}
check_attrs = {'class': 'form-control form-control-sm','style':'width: 1.5rem;'}
date_attrs = {'class':'form-control form-control-md rounded date-input','name':'date'}

class ReceivedInvoiceForm(ModelForm):
	class Meta:
		model = ReceivedInvoice
		widgets = {
		'associated_payment':forms.HiddenInput(),
		'amount': forms.NumberInput(attrs=reg_attrs),
		'number': forms.TextInput(attrs=reg_attrs),
		'date_received': forms.DateInput(format=DATE_INPUT_FORMATS[0], attrs=date_attrs),
		'pdf':forms.FileInput(attrs={'class': 'form-control-file'}),
		'is_paid': forms.CheckboxInput(attrs=check_attrs),
		}
		fields=list(widgets.keys())

class IssuedInvoiceForm(ModelForm):
	class Meta:
		model = IssuedInvoice
		widgets = {
		'associated_payment':forms.HiddenInput(),
		'amount': forms.NumberInput(attrs=reg_attrs),
		'number': forms.TextInput(attrs=reg_attrs),
		'date_issued': forms.DateInput(format=DATE_INPUT_FORMATS[0], attrs=date_attrs),
		'pdf':forms.FileInput(attrs={'class': 'form-control-file','type':'hidden'}),
		'is_paid': forms.CheckboxInput(attrs=check_attrs),
		}
		fields=list(widgets.keys())

	def clean(self):
		cleaned_data = super().clean()
		payment = cleaned_data['associated_payment']
		context = {'pagesize':'A4', **cleaned_data}
		invoice_file = make_pdf_preview('invoice/invoice.html', context)
		in_memory_kwargs = {
			'file':invoice_file,
			'name':'issued_invoice.pdf',
			'content_type':'application/pdf',
			'charset':None,
			'field_name':'pdf',
			'size':50
		}
		in_memory_obj = InMemoryUploadedFile(**in_memory_kwargs)
		cleaned_data['pdf'] = in_memory_obj
		return cleaned_data
