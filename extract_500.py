import pandas as pd

# This script will be updated with the actual translations in the next step
# for now I just want to extract the first 500 lines to make sure I have them all

df = pd.read_csv('data_processed/friends_quotes.csv', nrows=500)
df.to_csv('temp_quotes_to_translate.csv', index=False)
print(df.head())
