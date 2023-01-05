from datetime import datetime, timedelta
from my_app.models import *
import random
import pandas as pd
from django.db import transaction as tr
pd.options.display.float_format = '{:,.2f}'.format
green = '\u001b[32;1m'
cyan = '\u001b[36;1m'
yellow = '\u001b[33;1m'
reset = '\u001b[0m'
danger = '\u001b[31m\u001b[47m'

def get_random_date():
	'''Return a random date as a string between a start and end date'''
	start_date = datetime(2021, 3, 1)
	end_date = datetime(2041, 4, 1)
	time_between_dates = end_date - start_date
	days_between_dates = time_between_dates.days
	random_number_of_days = random.randrange(days_between_dates)
	random_date = start_date + timedelta(days=random_number_of_days)
	return random_date.strftime('%Y-%m-%d')


payment_count = 3
random_date_list = sorted([get_random_date() for i in range(payment_count)])
random_payment_list = [random.randint(10, 100) for i in range(payment_count)]
random_actuals_list = ['A' for i in range(payment_count)]


def calculate(payments=random_payment_list, dates=random_date_list, actuals=random_actuals_list, as_records=True):
	'''
	Generate IFRS16 calculations from a list of payments and a list of dates.
	If no arguments are supplied, random dummy data is generated and used.
	'''

	print(cyan+'Generating IFRS16 Calculations...', reset)
	print(yellow+'Monetary values in GBP', reset)
	payments = sorted([int(payment*Decimal('100')) for payment in payments])
	dates = sorted(dates)
	initial_date = dates[0]
	dates.insert(0, initial_date)
	initial_actual = actuals[0]
	actuals.insert(0, initial_actual)
	try:
		year_list = sorted([date[0:4] for date in dates])
	except:
		year_list = sorted([date.year for date in dates])
	time_periods = len(payments)
	base_year = 2021
	time_index_list = [int(year)-base_year+1 for year in year_list]
	time_index_list[0] = time_index_list[0]-1
	initial_payment = 0
	payments.insert(0, initial_payment)
	interest_rate = 0.009
	disc_factor_list = [(1/(1+interest_rate)**time_index) for time_index in time_index_list]
	zip_list = zip(payments, disc_factor_list)
	disc_payment_list = [payment*disc_factor for payment, disc_factor in zip_list]
	npv = sum(disc_payment_list)
	liability_list = [npv]
	depreciation_list = [npv/time_periods]*time_periods
	depreciation_list.insert(0, 0)
	interest_paid_list = [0]
	recognise_lease_list = [npv]
	group_list = ['Initial']
	for index, payment in enumerate(payments):
		if index == 0:
			continue
		group_list.append('Ongoing')
		prior_liability = liability_list[index-1]
		interest_paid = interest_rate * prior_liability
		new_liability = prior_liability + interest_paid - payment
		interest_paid_list.append(interest_paid)
		liability_list.append(new_liability)
		recognise_lease_list.append(0)

	def gbp(data_list):
		new_data_list = []
		for data in data_list:
			new_data = data/100
			new_data_list.append(new_data)
		return new_data_list
	print('Payments Count:', time_periods)
	print('Interest Rate:', str(interest_rate*100)+'%')
	print('Base Year:', base_year)
	payment_sum = sum(gbp(payments))
	depreciation_sum = sum(gbp(depreciation_list))
	interest_sum = sum(gbp(interest_paid_list))
	print('Sum of Payments:', f'{payment_sum:,}')
	print('Overall NPV:', f'{npv/100:,}')
	print('Sum of Interest Paid:', f'{interest_sum:,}')
	print('Sum of Depreciation:', f'{depreciation_sum:,}')
	difference = depreciation_sum + interest_sum - payment_sum
	if abs(difference) < 1E-5:
		message = green+'Total depreciation and interest equal total payments'
	else:
		message = danger + 'Total depreciation and interest do not equal total payments'
	print(message, reset, f'(difference = {difference:e})')

	data = {
		'Date': dates,
		'Time Index': time_index_list,
		'Discount Factor': disc_factor_list,
		'Discount Payment': gbp(disc_payment_list),
		'Group': group_list,
		'Recognise Lease': gbp(recognise_lease_list),
		'Depreciate Asset': gbp(depreciation_list),
		'Pay Interest': gbp(interest_paid_list),
		'Pay Cash': gbp(payments),
		'Liability': gbp(liability_list),
		'Actuals': actuals
	}
	df = pd.DataFrame(data)
	print(df, '', sep='\n')
	if as_records:
		multi_dict = df.to_dict('records')
		return multi_dict
	else:
		return data


def create_records(payments=None, dates=None, actuals=None, func=calculate, contract=None, transactions=None):
	start_time = datetime.now()
	if payments:
		multi_dict = func(payments=payments, dates=dates, actuals=actuals)
	else:
		multi_dict = func()
	transaction_list = []
	entry_list = []
	print(cyan+'Building TRANSACTION records...', reset)
	for period, data in enumerate(multi_dict):
		group_name = data['Group']
		group = TransactionGroup.objects.get(name=group_name)
		date = data['Date']
		time_index = data['Time Index']
		actual = data['Actuals']
		for transaction_type in group.transactiontype_set.all():
			amount = data[transaction_type.name]
			transaction_kwargs = {
				'transaction_type': transaction_type,
				'amount': amount,
				'date': date,
				'treatment': 'Accounting',
				'time_index': time_index,
				'contract': contract if contract else None,
				'actual_expected': actual
			}
			transaction = Transaction(**transaction_kwargs)
			transaction_list.append(transaction)
			print(transaction)
	db_transaction_list = []
	with tr.atomic():
		for t in transaction_list:
			t.save()
			db_transaction_list.append(t)
	print(green+'Saved TRANSACTION records', reset)
	print(cyan+'Building ENTRY records...', reset)
	for transaction in db_transaction_list:
		pseudoentry_set = transaction.transaction_type.pseudoentry_set.values()
		print(transaction)
		for entry in pseudoentry_set:
			entry.pop('id')
			entry.pop('transaction_type_id')
			entry['amount'] = transaction.amount
			entry['transaction'] = transaction
			entry_list.append(Entry(**entry))
			print(entry)
		print('\n')
	Entry.objects.bulk_create(entry_list)
	print(green+'Saved ENTRY records', reset)
	duration = datetime.now()-start_time
	print(green+'COMPLETED', 'in', str(duration), 'seconds', reset)
