import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn
df_1950_2017 = pd.read_csv('SAP500 historical prices 1950 - 2017.csv')
df_1978_present = pd.read_csv('SAP500 historical prices 1978 - present.csv')
df_1978_present = df_1978_present.iloc[::-1]
df_1978_present['Fifty_EMA'] = ""
df_1978_present['Twenty_EMA'] = ""
df_1978_present['Under/Over EMA'] = ""
df_1950_2017['Fifty_EMA'] = ""
df_1950_2017['Twenty_EMA'] = ""
df_1950_2017['Under/Over EMA'] = ""

# Find the last date's index at the 1978 to present dataframe
df_1978_present.drop([i for i in range(909, 10996)], inplace=True)

# Correct the column names
df_1978_present.rename(columns={' Open': 'Open', ' High': 'High', ' Low': 'Low', ' Close': 'Close'}, inplace=True)

# Concat the df
all_data_df = pd.concat([df_1950_2017, df_1978_present], axis=0)
all_data_df.set_index('Date', inplace=True)
all_data_df['One_day_yield'] = ""
all_data_df['Two_day_yield'] = ""
all_data_df['Three_day_yield'] = ""

# Get the wanted years
for i in all_data_df.iterrows():
    if i[0] == '1/2/1962':
        break
    all_data_df.drop(i[0], inplace=True)

# Handle the EMA
all_data_df['Fifty_EMA'] = all_data_df['Close'].ewm(span=50, adjust=False).mean()
all_data_df['Twenty_EMA'] = all_data_df['Close'].ewm(span=20, adjust=False).mean()
for i in list(all_data_df.index.values):
    if all_data_df.at[i, 'Twenty_EMA'] > all_data_df.at[i, 'Fifty_EMA']:
        all_data_df.at[i, 'Under/Over EMA'] = 'Over'
    elif all_data_df.at[i, 'Twenty_EMA'] < all_data_df.at[i, 'Fifty_EMA']:
        all_data_df.at[i, 'Under/Over EMA'] = 'Under'
    else:  # Equal
        all_data_df.at[i, 'Under/Over EMA'] = None

# Handle the yields
index_lst = list(all_data_df.index.values)
for i in range(len(index_lst)):
    if i > 1:  # One day yield
        if all_data_df.at[index_lst[i - 1], 'Close'] > all_data_df.at[index_lst[i - 2], 'Close']:
            all_data_df.at[index_lst[i], 'One_day_yield'] = 'Up'
        elif all_data_df.at[index_lst[i - 1], 'Close'] < all_data_df.at[index_lst[i - 2], 'Close']:
            all_data_df.at[index_lst[i], 'One_day_yield'] = 'Down'
        else:  # Equal
            all_data_df.at[index_lst[i], 'One_day_yield'] = 'Equal'
    if i > 2:  # Two day yield
        if all_data_df.at[index_lst[i - 1], 'Close'] > all_data_df.at[index_lst[i - 3], 'Close']:
            all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Up'
        elif all_data_df.at[index_lst[i - 1], 'Close'] < all_data_df.at[index_lst[i - 3], 'Close']:
            all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Down'
        else:  # Equal
            all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Equal'
    if i > 3:  # Three day yield
        if all_data_df.at[index_lst[i - 1], 'Close'] > all_data_df.at[index_lst[i - 4], 'Close']:
            all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Up'
        elif all_data_df.at[index_lst[i - 1], 'Close'] < all_data_df.at[index_lst[i - 4], 'Close']:
            all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Down'
        else:  # Equal
            all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Equal'
    # Handle beginnings
    if i == 0:
        all_data_df.at[index_lst[i], 'One_day_yield'] = 'Equal'
        all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Equal'
        all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Equal'
    if i == 1:
        all_data_df.at[index_lst[i], 'One_day_yield'] = 'Equal'
        all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Equal'
        all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Equal'
    if i == 2:
        all_data_df.at[index_lst[i], 'Two_day_yield'] = 'Equal'
        all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Equal'
    if i == 3:
        all_data_df.at[index_lst[i], 'Three_day_yield'] = 'Equal'


# Handle the rates
rates_df = pd.read_csv('rates_new.csv')
rates_df.rename(columns={'DATE': 'Date'}, inplace=True)
rates_df.rename(columns={'DGS10': 'Rate'}, inplace=True)
for i in range(rates_df.__len__()):
    if rates_df['Rate'][i] == '.':
        temp = rates_df['Rate'][i-1]
        rates_df['Rate'][i] = temp

# Handle the EMA in the rates dataframe
rates_df['Fifty_EMA'] = rates_df['Rate'].ewm(span=50, adjust=False).mean()
rates_df['Twenty_EMA'] = rates_df['Rate'].ewm(span=20, adjust=False).mean()
rates_df['Under/Over EMA'] = ''
for i in list(rates_df.index.values):
    if rates_df.at[i, 'Twenty_EMA'] > rates_df.at[i, 'Fifty_EMA']:
        rates_df.at[i, 'Under/Over EMA'] = 'Over'
    elif rates_df.at[i, 'Twenty_EMA'] < rates_df.at[i, 'Fifty_EMA']:
        rates_df.at[i, 'Under/Over EMA'] = 'Under'
    else:  # Equal
        rates_df.at[i, 'Under/Over EMA'] = None

# Make sure the dates are the same
rates_index_list = rates_df['Date'].tolist()
problem_list = []
for i in rates_index_list:
    if i not in index_lst:
        problem_list.append(i)

rates_df.set_index('Date', inplace=True)
for i in problem_list:
    rates_df.drop(i, inplace=True)

problem_list = []
rates_index_list = list(rates_df.index.values)
for i in rates_index_list:
    if i not in index_lst:
        problem_list.append(i)

# Split to Experiment and Test
count = 0
for i in all_data_df.iterrows():
    if i[0] != '1/2/2015':
        count += 1
    else:
        break
split_date = count
experiment_df = all_data_df.iloc[:split_date]
test_df = all_data_df.iloc[split_date:]

# Split the rates df
count = 0
for i in rates_df.iterrows():
    if i[0] != '1/2/2015':
        count += 1
    else:
        break
rate_split_Date = count
rates_experiment_df = rates_df.iloc[:rate_split_Date]
rates_test_df = rates_df.iloc[rate_split_Date:]
