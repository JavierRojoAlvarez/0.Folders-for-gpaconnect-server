import urllib.request
import json
import pandas as pd
from datetime import datetime

pd.options.mode.chained_assignment = None

def tracker():
	url="https://opendata.ecdc.europa.eu/covid19/casedistribution/json/"
	with urllib.request.urlopen(url) as url:
		data = json.loads(url.read().decode())
		df=pd.json_normalize(data,record_path='records')
	print(list(df))
	df['dateRep'] = pd.to_datetime(df['dateRep'],format='%d/%m/%Y')
	num_cols = pd.Index(['cases','deaths','popData2019'])
	df[num_cols] = df[num_cols].apply(pd.to_numeric, errors='coerce')
	df.set_index('dateRep',inplace=True)


	condition_uk = (df['countryterritoryCode']=='GBR')
	df_uk = df[condition_uk]
	df_uk = df_uk.sort_index(ascending=True, axis=0)
	df_uk['cumulative_cases'] = df_uk['cases'].cumsum()

	data = {
		'labels':df_uk.index.to_list(),
		'values':df_uk['cumulative_cases'].to_list()
	}
	return data
