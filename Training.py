import pandas as pd
import main as main
import random
experiment_df = main.experiment_df
rates_experiment_df = main.rates_experiment_df
situation_bank = main.situation_bank

# Training Phase
tries = 0
# Load the last run
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
# Create a csv with all the details
economic_data = {"Date": [i for i in experiment_df["Date"]],
                 "Closing Day Market Value": [i for i in experiment_df["Close"]],
                 "Stay or Change Decision": ["a" for i in experiment_df.index.values],
                 "Market Decision": ["a" for i in experiment_df.index.values],
                 "Current Portfolio Value": ["a" for i in experiment_df.index.values],
                 "Current Draw Down": ["a" for i in rates_experiment_df['Under/Over EMA']],
                 "Under/Over EMA": [i for i in experiment_df['Under/Over EMA']],
                 "Under/Over EMA Rates": [i for i in rates_experiment_df['Under/Over EMA']],
                 "One Day Yield": [i for i in experiment_df["One_day_yield"]],
                 "Two Day Yield": [i for i in experiment_df["Two_day_yield"]],
                 "Three Day Yield": [i for i in experiment_df["Three_day_yield"]]}
economic_data_df = pd.DataFrame(economic_data)
# Set the last best settings
temp_best_long_situation_bank = [i for i in long_situation_bank]
temp_best_short_situation_bank = [i for i in short_situation_bank]
temp_best_out_situation_bank = [i for i in out_situation_bank]
# Create the csv to save the next best runs
improvement_data = {"Index": [i for i in situation_bank],
                    "Situation": [str(i) for i in situation_bank],
                    "Market Decision": ["" for i in situation_bank]}
improvement_df = pd.DataFrame(improvement_data)
improvement_df.set_index('Index', inplace=True)
# Set the base, in order to compare with every run
last_run_long_index_list = []
last_run_short_index_list = []
last_run_out_index_list = []
for i in list(experiment_df.index.values):
    situation = main.Identifier(i, rates_experiment_df, experiment_df)
    if situation in long_situation_bank:
        last_run_long_index_list.append(i)
    elif situation in short_situation_bank:
        last_run_short_index_list.append(i)
    elif situation in out_situation_bank:
        last_run_out_index_list.append(i)
base = main.Market_Action(last_run_long_index_list,
                          last_run_short_index_list,
                          experiment_df.index.values,
                          experiment_df,
                          economic_data_df,
                          start_sum=10000)
economic_data_df.to_csv('Best_Strategy_Economic_Data.csv')
# Determine whether to start changing from the first run or not
change_bool = True
print("base is", base)
# Start the training process
while tries < 5:
    long_index_list = []
    short_index_list = []
    out_index_list = []
    # Decide which situations to change
    change_set = set()
    change_lst = []
    while len(change_set) < 5:
        if change_bool is False:
            break
        change_set.add(random.randint(0, 242))
    for i in change_set:
        decider = random.randint(0, 2)
        temp_tuple = (i, decider)
        change_lst.append(temp_tuple)
    # Move the situations between the banks. If the situation was already in one bank, remove it.
    for i in change_lst:
        situation_num = situation_bank[i[0]]
        # Go long
        if i[1] == 0 and situation_num not in long_situation_bank:
            long_situation_bank.append(situation_num)
            # Get out of short and out
            if situation_num in short_situation_bank:
                short_situation_bank.remove(situation_num)
            if situation_num in out_situation_bank:
                out_situation_bank.remove(situation_num)
        # Go short
        elif i[1] == 1 and situation_num not in short_situation_bank:
            short_situation_bank.append(situation_num)
            # Get out of long and out
            if situation_num in long_situation_bank:
                long_situation_bank.remove(situation_num)
            if situation_num in out_situation_bank:
                out_situation_bank.remove(situation_num)
        # Go out
        elif i[1] == 2 and situation_num not in out_situation_bank:
            out_situation_bank.append(situation_num)
            # Get out of long and short
            if situation_num in long_situation_bank:
                long_situation_bank.remove(situation_num)
            if situation_num in short_situation_bank:
                short_situation_bank.remove(situation_num)
    # The rest go to long (will only do something in the first run)
    for i in situation_bank:
        if i not in long_situation_bank and i not in short_situation_bank and i not in out_situation_bank:
            long_situation_bank.append(i)
    # Translate the codes to actual indices
    for i in list(experiment_df.index.values):
        situation = main.Identifier(i, rates_experiment_df, experiment_df)
        if situation in long_situation_bank:
            long_index_list.append(i)
        elif situation in short_situation_bank:
            short_index_list.append(i)
    # If the new try is better, save it. Otherwise, try again
    res = main.Market_Action(long_index_list,
                             short_index_list,
                             experiment_df.index.values,
                             experiment_df,
                             economic_data_df,
                             start_sum=10000)
    print(res)
    change_bool = True
    if res[1] == 1 and res[0] > base[0]:
        tries += 1
        print("\n", "Improvement number", tries, "\n")
        base = res
        temp_best_long_situation_bank = [i for i in long_situation_bank]
        temp_best_short_situation_bank = [i for i in short_situation_bank]
        temp_best_out_situation_bank = [i for i in out_situation_bank]
        for item in improvement_df.iterrows():
            if item[0] in long_situation_bank:
                improvement_df.at[item[0], 'Market Decision'] = "Long"
            elif item[0] in short_situation_bank:
                improvement_df.at[item[0], 'Market Decision'] = "Short"
            elif item[0] in out_situation_bank:
                improvement_df.at[item[0], 'Market Decision'] = "Out"
        improvement_df.to_csv('Best_Strategy.csv')
        # Overwrite the details csv
        economic_data_df.to_csv('Best_Strategy_Economic_Data.csv')
    elif res[0] <= base[0]:
        print("No change, currently at improvement number", tries)
        long_situation_bank = [i for i in temp_best_long_situation_bank]
        short_situation_bank = [i for i in temp_best_short_situation_bank]
        out_situation_bank = [i for i in temp_best_out_situation_bank]
print(res)
