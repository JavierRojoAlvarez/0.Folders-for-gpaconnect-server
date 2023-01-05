from django.db import models
from my_app.models import *
from django.core.validators import MinValueValidator
from invoice.validators import validate_is_pdf
from decimal import Decimal

class AbstractInvoice(models.Model):
	associated_payment = models.ForeignKey(ContractPayment,on_delete=models.CASCADE, default='',verbose_name='Associated Payment')
	amount = models.DecimalField(decimal_places=2,max_digits=20, default=0,validators=[MinValueValidator(Decimal('0.00'))])
	class Meta:
		abstract=True
		verbose_name_plural='Abstract Invoices'

class ReceivedInvoice(AbstractInvoice):
	number=models.CharField('Invoice Number',max_length=50,default='')
	date_received = models.DateField('Date Received')
	pdf = models.FileField('PDF File',upload_to='received-invoices/', validators=(validate_is_pdf,))
	is_paid = models.BooleanField('Paid by GPA',default=False)
	def __str__(self):
		return str(self.date_received)+':'+str(self.amount)
	class Meta:
		verbose_name_plural='Received Invoices'

class IssuedInvoice(AbstractInvoice):
	number=models.CharField('Invoice Number',max_length=50,default='')
	date_issued = models.DateField('Date Issued')
	pdf = models.FileField('PDF File',upload_to='issued-invoices/',blank=True)
	is_paid = models.BooleanField('Paid by customer',default=False)
	def __str__(self):
		return str(self.date_issued)+':'+str(self.amount)
	class Meta:
		verbose_name_plural='Issued Invoices'
