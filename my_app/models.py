from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator
from decimal import Decimal
from website.settings import DATE_INPUT_FORMATS


class Region(models.Model):
	name = models.CharField(max_length=30, default='')

	def __str__(self):
		return self.name


class Building(models.Model):
	epims_id = models.CharField('ePIMS ID', max_length=50)
	name = models.CharField('Name', max_length=50)
	region = models.ForeignKey(Region, on_delete=models.CASCADE, default='')
	nia = models.DecimalField('NIA', decimal_places=2, max_digits=20, default=0)
	ftes_capacity = models.DecimalField('FTEs Capacity', decimal_places=2,
										max_digits=20, default=0)
	image = models.ImageField(default='images/default.png', upload_to='images')
	cost_centre = models.CharField('Cost Centre', max_length=50, default='')

	def __str__(self):
		return self.name


class CostType(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Cost Types'


class Cost(models.Model):
	start = models.DateField()
	end = models.DateField()
	cost_type = models.ForeignKey(CostType, on_delete=models.CASCADE, default='')
	building = models.ForeignKey(Building, on_delete=models.CASCADE, default='')
	option = models.IntegerField()
	value = models.DecimalField(decimal_places=2, max_digits=20, default=0)

	def __str__(self):
		return str(self.cost_type) + ':' + str(self.start)


class AccountType(models.Model):
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Account Types'


class Hierarchy1(models.Model):
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name


class Hierarchy2(models.Model):
	hierarchy1 = models.ForeignKey(Hierarchy1, on_delete=models.CASCADE,
								   default='')
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name


class Hierarchy3(models.Model):
	hierarchy2 = models.ForeignKey(Hierarchy2, on_delete=models.CASCADE,
								   default='')
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name


class Hierarchy4(models.Model):
	hierarchy3 = models.ForeignKey(Hierarchy3, on_delete=models.CASCADE,
								   default='')
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name


class Account(models.Model):
	number = models.IntegerField()
	account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE)
	hierarchy4 = models.ForeignKey(Hierarchy4, on_delete=models.CASCADE)
	description = models.CharField(max_length=50, default='')
	is_live = models.BooleanField('Live', default=True)

	class Meta:
		ordering = ('description',)

	def __str__(self):
		return self.description


class Direction(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name


class AbstractEntry(models.Model):
	direction = models.ForeignKey(Direction, on_delete=models.CASCADE,
								  default='')
	account = models.ForeignKey(Account, on_delete=models.CASCADE, default='')
	amount = models.DecimalField(decimal_places=2, max_digits=20, default=0,
								 validators=[MinValueValidator(Decimal('0.00'))])

	def __str__(self):
		return str(self.direction)+':'+str(self.account)+':'+str(self.amount)

	class Meta:
		abstract = True
		verbose_name_plural = 'Abstract Entries'


class TransactionGroup(models.Model):
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name

		class Meta:
			verbose_name_plural = 'Entry Groups'


class TransactionType(models.Model):
	name = models.CharField(max_length=50, default='')
	group = models.ForeignKey(TransactionGroup, on_delete=models.CASCADE,
							  default='', null=True, blank=True,
							  verbose_name='Transaction Group')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Transaction Types'


class PseudoEntry(AbstractEntry):
	transaction_type = models.ForeignKey(TransactionType,
										 on_delete=models.CASCADE, default='',
										 verbose_name='Transaction Type')
	amount = models.DecimalField(decimal_places=2, max_digits=20, default=0)

	def __str__(self):
		return str(self.transaction_type.name)
		+' / '
		+str(self.direction)
		+':'+str(self.account)

	class Meta:
		verbose_name_plural = 'Pseudo Entries'


class OrganisationType(models.Model):
	name = models.CharField(max_length=50)

	class Meta:
		verbose_name_plural = 'Organisation Types'


class Organisation(models.Model):
	name = models.CharField(max_length=50)
	organisation_type = models.ForeignKey(OrganisationType,
										  on_delete=models.CASCADE, null=True,
										  blank=True)
	reference = models.IntegerField()
	sort_code = models.IntegerField()
	account_number = models.IntegerField()
	postcode = models.CharField(max_length=50, default='')
	address = models.TextField(max_length=200, default='')

	def __str__(self):
		return self.name


class AssetType(models.Model):
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Asset Types'


class ProfitCentre(models.Model):
	name = models.IntegerField()

	def __str__(self):
		return str(self.name)

	class Meta:
		verbose_name_plural = 'Profit Centres'


class ContractType(models.Model):
	name = models.CharField(max_length=50, default='')

	def __str__(self):
		return self.name

	class Meta:
		verbose_name_plural = 'Contract Types'


class Contract(models.Model):
	REVENUE_EXPENDITURE = (('R', 'Revenue'), ('E', 'Expenditure'))
	TREATMENT = (('Lessee', 'Lessee'), ('Lessor', 'Lessor'))
	description = models.CharField(max_length=50)
	revenue_expenditure = models.CharField(
		'Revenue/Expenditure', max_length=50, choices=REVENUE_EXPENDITURE)
	contract_type = models.ForeignKey(ContractType, on_delete=models.CASCADE,
									  null=True, blank=True,
									  verbose_name='Contract Type')
	organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE,
									 null=True, blank=True,
									 verbose_name='Counterparty')
	building = models.ManyToManyField(Building, blank=True)
	treatment = models.CharField('Treatment', max_length=50, null=True,
								 blank=True, choices=TREATMENT)
	start = models.DateField(null=True, blank=True)
	end = models.DateField(null=True, blank=True)
	signed = models.BooleanField(default=False)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		if self.contract_type:
			return self.contract_type.name+':'+self.description+' ['
			+str(self.start_date)+' to '+str(self.end_date)+' ]'
		else:
			return self.description+' ['+str(self.start_date)+' to '
			+str(self.end_date)+' ]'

	@property
	def npv(self):
		record = self.transaction_set.get(
			transaction_type__name='Recognise Lease')
		npv = record.amount
		return npv

	@property
	def total_payments(self):
		qs = self.contractpayment_set.all()
		total_payments = qs.aggregate(Sum('amount'))['amount__sum']
		return total_payments

	@property
	def total_interest(self):
		qs = self.transaction_set.filter(transaction_type__name='Pay Interest')
		total_interest = qs.aggregate(Sum('amount'))['amount__sum']
		return total_interest

	@property
	def start_date(self):
		qs = self.transaction_set.order_by('date')
		try:
			start_date = qs.first().date
			return start_date
		except:
			return

	@property
	def end_date(self):
		qs = self.transaction_set.order_by('date')
		try:
			end_date = qs.last().date
			return end_date
		except:
			return


class Transaction(models.Model):
	TREATMENT = (('Accounting', 'Accounting'), ('Budgeting', 'Budgeting'))
	ACTUAL_EXPECTED = (('E', 'Expected'), ('A', 'Actual'))
	date = models.DateField()
	transaction_type = models.ForeignKey(TransactionType,
										 on_delete=models.CASCADE, null=True,
										 blank=True,
										 verbose_name='Transaction Type')
	comment = models.TextField(max_length=200, default='', null=True,
													   blank=True)
	contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True,
								 blank=True)
	actual_expected = models.CharField('Actual/Expected', max_length=50,
									   choices=ACTUAL_EXPECTED, default='E')
	period = models.CharField(max_length=50, null=True, blank=True)
	amount = models.DecimalField(decimal_places=2, max_digits=20, default=0,
								 null=True,
								 validators=[MinValueValidator(Decimal('0.01'))])
	treatment = models.CharField('Treatment', max_length=50, choices=TREATMENT,
								 null=True, blank=True, default='')
	time_index = models.IntegerField(null=True, blank=True, default=0)

	def __str__(self):
		return str(self.transaction_type) + ':' + str(self.date)


class ContractPayment(models.Model):
	TREATMENT = (('Accounting', 'Accounting'), ('Budgeting', 'Budgeting'))
	ACTUAL_EXPECTED = (('E', 'Expected'), ('A', 'Actual'))
	date = models.DateField(null=True, blank=True)
	transaction_type = models.ForeignKey(TransactionType,
										 on_delete=models.CASCADE, null=True,
										 blank=True,
										 verbose_name='Transaction Type')
	comment = models.TextField(max_length=200, default='', null=True, blank=True)
	contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True,
								 blank=True)
	actual_expected = models.CharField('Actual/Expected', max_length=50,
									   choices=ACTUAL_EXPECTED, default='E')
	period = models.CharField(max_length=50, null=True, blank=True)
	amount = models.DecimalField(decimal_places=2, max_digits=20, default=0,
								 null=True,
								 validators=[MinValueValidator(Decimal('0.01'))])
	treatment = models.CharField('Treatment', max_length=50, choices=TREATMENT,
								 null=True, blank=True, default='')
	time_index = models.IntegerField(null=True, blank=True, default=0)

	def __str__(self):
		return str(self.transaction_type) + ':' + str(self.date)


class Entry(AbstractEntry):
	transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE,
									null=True, blank=True, default='')
	contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
								 null=True, blank=True, default='')
	liability = models.DecimalField(decimal_places=2, max_digits=20, default=0,
									null=True)

	@property
	def signed_amount(self):
		positive = ['Buildings Cost', 'Rent Expenditure', 'Bank Account']
		negative = ['Deferred Expense (Lease)', 'Rent Recovery',
					'OB General Fund']
		if self.account.description in positive:
			account_sign = 1
		elif self.account.description in negative:
			account_sign = -1
		if self.direction.name == 'Debit':
			direction_sign = 1
		else:
			direction_sign = -1
		return account_sign * direction_sign * self.amount

	class Meta:
		verbose_name_plural = 'entries'
