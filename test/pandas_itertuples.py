import pandas as pd
import numpy as np


df = pd.DataFrame({'col1': [1, 2], 'col2': [0.1, 0.2]}, index=['a', 'b'])
print (df)
for row in df.itertuples(name=None):
    print(row)
for row in df.itertuples():
    print(row)
    print(row.col1)