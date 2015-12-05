from datetime import datetime
import pandas as pd

dateparser = lambda x: datetime.strptime(x, '%d.%m.%Y %H:%M')

df = pd.read_csv('Farge-ALL_10min.all', parse_dates=['Datetime'], sep=';', date_parser=dateparser, decimal='.', usecols=[1, 2, 3, 4, 5, 6, 7], header=0, skiprows=1, index_col=0)


df.index.to_julian_date().values
df.index[0].to_datetime()

for i in xrange (nIndices):
    (df.index[i].to_datetime()-datetime(1970, 1, 1)).total_seconds()
