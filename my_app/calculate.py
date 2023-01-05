from .models import Cost, Building
from django_pandas.io import read_frame
import numpy as np
import pandas as pd
import time
from datetime import datetime

def calculate(cost_qs=Cost.objects.filter(building__id=4),building_qs=Building.objects.all(),groupby=False):
	start_time = datetime.now()
	print(start_time)
	print('Recalculating...')
	cost_df=read_frame(cost_qs,verbose=False)
	print(cost_df.shape)
	building_df=read_frame(building_qs,verbose=False)
	cost_df['value']=cost_df['value'].astype('float')
	t = np.arange('2020-04', '2046-04', 3, dtype='datetime64[M]')
	base_fy_start=2020
	y = np.arange(0,len(cost_df))
	period_start=np.tile(t, len(y))
	period_end=period_start+np.timedelta64(3, 'M')-np.timedelta64(1, 'D')
	period_dur=(period_end-period_start+1).astype(int)
	year = period_start.astype('datetime64[Y]').astype(int) + 1970
	month = period_start.astype('datetime64[M]').astype(int) % 12 + 1
	fy_start=np.where(month!=1,year,year-1)
	time_index=fy_start-base_fy_start
	cross_index=np.repeat(y, len(t))
	start=cost_df['start'].values.astype('datetime64[D]')
	end=cost_df['end'].values.astype('datetime64[D]')
	start=np.repeat(start,len(t))
	end=np.repeat(end,len(t))
	span=(np.minimum(period_end,end)-np.maximum(period_start,start)).astype(int)
	span=np.where(span>=0,span+1,span)
	period_frac=span/period_dur
	lump_sum=np.where(start==end, True, False)
	vector_list=[period_start, period_end, period_dur, fy_start, time_index,cross_index, period_frac, lump_sum]
	data_array=np.transpose(vector_list)
	column_list=['period_start', 'period_end', 'period_dur', 'fy_start', 'time_index','cross_index', 'period_frac', 'lump_sum']
	df=pd.DataFrame(data=data_array,columns=column_list)
	in_date_condition=df['period_frac']>0
	df=df[in_date_condition]
	df=df.merge(cost_df,left_on='cross_index', right_index=True)
	df=df.merge(building_df,left_on='building', right_index=True)
	df['fy_string']=df['fy_start'].map(str)+"/"+(df['fy_start']+1).map(str)
	df['value_norm']=(df['value']/4).where(df['lump_sum']==False,df['value'])
	df['value_norm']=(df['value_norm']*df['period_frac']).where(df['lump_sum']==False,df['value_norm'])
	if groupby:
		df=df.groupby(groupby,as_index=False).agg({'value_norm':'sum'})
	data=df.to_dict('records')
	print(df.columns)
	print('Rows, Columns = '+str(df.shape))
	print('Datapoints = '+str(df.size))
	print('Calculation Complete!')
	duration=datetime.now()-start_time
	print('Duration: '+str(duration))

	return data
