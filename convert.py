import pandas as pd


df = pd.read_csv('hoildayLoungeData.tsv', sep='\t')


df.to_excel('hoildayLoungeData.xlsx', index=False)