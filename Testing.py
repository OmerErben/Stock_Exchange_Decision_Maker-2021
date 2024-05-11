import pandas as pd
import main as main
test_df = main.test_df
rates_test_df = main.rates_test_df
situation_bank = main.situation_bank

# Testing Phase
# Load the best strategy found so far
last_run_df = pd.read_csv('Best_Strategy.csv')
long_situation_bank = []
short_situation_bank = []
out_situation_bank = []
for i in list(last_run_df.index.values):
    situation = str(last_run_df.at[i, "Situation"])
    while len(situation) < 5:
        situation = "0" + situation
    if last_run_df.at[i, 'Market Decision'] == "Long":
        long_situation_bank.append(situation)
    elif last_run_df.at[i, 'Market Decision'] == "Short":
        short_situation_bank.append(situation)
    elif last_run_df.at[i, 'Market Decision'] == "Out":
        out_situation_bank.append(situation)
# Create a csv with all the economic details
economic_test_data = {"Date": [i for i in test_df["Date"]],
                      "Closing Day Market Value": [i for i in test_df["Close"]],
                      "Stay or Change Decision": ["a" for i in test_df.index.values],
                      "Market Decision": ["a" for i in test_df.index.values],
                      "Current Portfolio Value": ["a" for i in test_df.index.values],
                      "Current Draw Down": ["a" for i in rates_test_df['Under/Over EMA']],
                      "Under/Over EMA": [i for i in test_df['Under/Over EMA']],
                      "Under/Over EMA Rates": [i for i in rates_test_df['Under/Over EMA']],
                      "One Day Yield": [i for i in test_df["One_day_yield"]],
                      "Two Day Yield": [i for i in test_df["Two_day_yield"]],
                      "Three Day Yield": [i for i in test_df["Three_day_yield"]]}
economic_test_data_df = pd.DataFrame(economic_test_data)
# Start the testing process
long_index_list = []
short_index_list = []
out_index_list = []
# Translate the codes to actual indices
for i in list(test_df.index.values):
    situation = main.Identifier(i, rates_test_df, test_df)
    if situation in long_situation_bank:
        long_index_list.append(i)
    elif situation in short_situation_bank:
        short_index_list.append(i)
# Run the test
test = main.Market_Action(long_index_list,
                          short_index_list,
                          test_df.index.values,
                          test_df,
                          economic_test_data_df,
                          start_sum=10000)
economic_test_data_df.to_csv('Test_Economic_Data.csv')
print(test)
