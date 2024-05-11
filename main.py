import Data_Prep as Prep
import random
test_df = Prep.test_df
experiment_df = Prep.experiment_df
rates_test_df = Prep.rates_test_df
rates_experiment_df = Prep.rates_experiment_df
experiment_df.reset_index(inplace=True)
rates_experiment_df.reset_index(inplace=True)
test_df.reset_index(inplace=True)
rates_test_df.reset_index(inplace=True)
experiment_df.to_csv("experiment_df.csv")

# Create the long and short functions


def long(long_index_list, dataframe):
    indicator = False
    if long_index_list == []:
        return 0
    cur_sum = 0
    start = long_index_list[0]
    for i in range(1, len(long_index_list)):
        if long_index_list[i] == (long_index_list[i - 1] + 1):
            continue
        else:
            cur_sum -= dataframe.at[start, 'Close']
            cur_sum += dataframe.at[i, 'Close']
            start = long_index_list[i+1]
            indicator = True
    if indicator is False:
        cur_sum = (dataframe.at[long_index_list[-1], 'Close'] - dataframe.at[long_index_list[start], 'Close'])
    return cur_sum


def short(short_index_list, dataframe):
    indicator = False
    if short_index_list == []:
        return 0
    cur_sum = 0
    start = short_index_list[0]
    for i in range(1, len(short_index_list)):
        if short_index_list[i] == (short_index_list[i-1] + 1):
            continue
        else:
            cur_sum += dataframe.at[start, 'Close']
            cur_sum -= dataframe.at[i, 'Close']
            start = short_index_list[i+1]
            indicator = True
    if indicator is False:
        cur_sum = (dataframe.at[start, 'Close'] - dataframe.at[short_index_list[-1], 'Close'])
    return cur_sum

# Market decision for the second attempt


def Market_Action(long_index_list, short_index_list, all_dates_list, dataframe, economic_dataframe, start_sum=10000):
    num_of_stocks = 0
    cur_cash = start_sum
    max_cash = start_sum
    indicator = "Stay"
    decision = "Out"
    max_drawdown_allowed = 0
    cur_drawdown = 0
    max_drawdown = 0
    pos_month_yield_list = []
    neg_month_yield_list = []
    pos_year_yield_list = []
    neg_year_yield_list = []
    old_month = ""
    old_year = ""
    for i in range(len(all_dates_list)):
        # Figure out what we want to do
        if i in long_index_list:
            temp = "Long"
            if temp == decision:
                indicator = "Stay"
            else:
                old_decision = decision
                decision = temp
                indicator = "Change"
        elif i in short_index_list:
            temp = "Short"
            if temp == decision:
                indicator = "Stay"
            else:
                old_decision = decision
                decision = temp
                indicator = "Change"
        else:  # Out
            temp = "Out"
            if temp == decision:
                indicator = "Stay"
            else:
                old_decision = decision
                decision = temp
                indicator = "Change"
        # If we want to stay, figure out how much money we have
        if indicator == "Stay":
            if num_of_stocks != 0:
                if decision == "Long":
                    cur_cash = num_of_stocks * dataframe.at[i, 'Close']
                elif decision == "Short":
                    cur_cash = cur_cash + (num_of_stocks * dataframe.at[i - 1, 'Close']) - (
                                num_of_stocks * dataframe.at[i, 'Close'])
            if max_cash < cur_cash:
                max_cash = cur_cash
            if (max_drawdown_allowed * max_cash) > cur_cash:
                print("Fallen bellow the maximum Draw Down allowed. Bad strategy. The date is", dataframe.at[i, 'Date'])
                print("The total value of the portfolio is", cur_cash, "\n",
                      "The max value of the portfolio was", max_cash)
                return cur_cash, 0
        # If we want to change strategy
        elif indicator == "Change":
            # Get out of the last position
            if old_decision == "Long":
                cur_cash = num_of_stocks * dataframe.at[i, 'Close']
            elif old_decision == "Short":
                cur_cash = cur_cash + (num_of_stocks * dataframe.at[i - 1, 'Close']) - (num_of_stocks * dataframe.at[i, 'Close'])
            # elif old_decision == "Out":
                # None
            # Get into the next position
            if decision == "Long":
                num_of_stocks = cur_cash / dataframe.at[i, 'Close']
            elif decision == "Short":
                num_of_stocks = cur_cash / dataframe.at[i, 'Close']
            elif decision == "Out":
                num_of_stocks = 0
            if max_cash < cur_cash:
                max_cash = cur_cash
            if (max_drawdown_allowed * max_cash) > cur_cash:
                print("Fallen bellow the maximum Draw Down allowed. Bad strategy. The date is", dataframe.at[i, 'Date'])
                print("The total value of the portfolio is", cur_cash, "\n",
                      "The max value of the portfolio was", max_cash)
                return cur_cash, 0
        # Get the monthly yield
        cur_month = dataframe.at[i, 'Date'].split("/")[0]
        if old_month == "":
            old_month = cur_month
            old_monthly_cash = cur_cash
        elif old_month != cur_month:
            # The month has changed
            month_yield = ((cur_cash / old_monthly_cash) - 1) * 100
            if month_yield < 0:
                neg_month_yield_list.append(month_yield)
            elif month_yield > 0:
                pos_month_yield_list.append(month_yield)
            old_month = cur_month
            old_monthly_cash = cur_cash
        # Get the yearly yield
        cur_year = dataframe.at[i, 'Date'].split("/")[2]
        if old_year == "":
            old_year = cur_year
            old_yearly_cash = cur_cash
        elif old_year != cur_year:
            # The year has changed
            year_yield = ((cur_cash / old_yearly_cash) - 1) * 100
            if year_yield < 0:
                neg_year_yield_list.append(year_yield)
            elif year_yield > 0:
                pos_year_yield_list.append(year_yield)
            old_year = cur_year
            old_yearly_cash = cur_cash
        # Update the most extreme drawdown
        cur_drawdown = ((cur_cash / max_cash) - 1) * 100
        if cur_drawdown < max_drawdown:
            max_drawdown = cur_drawdown
        # Update the economic data
        economic_dataframe.at[i, "Stay or Change Decision"] = indicator
        economic_dataframe.at[i, "Market Decision"] = decision
        economic_dataframe.at[i, "Current Portfolio Value"] = cur_cash
        economic_dataframe.at[i, "Current Draw Down"] = cur_drawdown
    if len(neg_year_yield_list) > 0:
        pain_to_gain_yearly = (sum(pos_year_yield_list)) / (abs(sum(neg_year_yield_list)))
    else:
        pain_to_gain_yearly = 0
    if len(neg_month_yield_list) > 0:
        pain_to_gain_monthly = (sum(pos_month_yield_list)) / (abs(sum(neg_month_yield_list)))
    else:
        pain_to_gain_monthly = 0
    years_passed = (int(cur_year) - int(dataframe.at[0, "Date"].split("/")[2]) +
                    (30 * (int(cur_month) - int(dataframe.at[0, "Date"].split("/")[0])) +
                    int(dataframe.at[all_dates_list[-1], "Date"].split("/")[1]) - int(dataframe.at[0, "Date"].split("/")[1])) / 365)
    IRR = (((cur_cash / start_sum) ** (1 / years_passed)) - 1) * 100
    print("The total value of the portfolio is", format(cur_cash, ".2f"),
          ", the Pain to Gain monthly is", format(pain_to_gain_monthly, ".2f"),
          "% , the Pain to Gain yearly is", format(pain_to_gain_yearly, ".2f"),
          "% , the Maximum Draw Down is", format(max_drawdown, ".2f"),
          "% and the IRR is", format(IRR, ".2f"), "%")
    return cur_cash, 1


long_index_list = []
short_index_list = []

# Define an identifier function which will return the current situation of the stock


def Identifier(index, rates_df, df):
    res = ""
    # Rates EMA
    if rates_df.iloc[index]['Under/Over EMA'] == "Under":
        res += "0"
    elif rates_df.iloc[index]['Under/Over EMA'] == "Over":
        res += "1"
    else:  # None
        res += "2"
    # Value EMA
    if df.iloc[index]['Under/Over EMA'] == "Under":
        res += "0"
    elif df.iloc[index]['Under/Over EMA'] == "Over":
        res += "1"
    else:  # None
        res += "2"
    # One_day_yield
    if df.iloc[index]['One_day_yield'] == "Down":
        res += "0"
    elif df.iloc[index]['One_day_yield'] == "Up":
        res += "1"
    else:  # Equal
        res += "2"
    # Two_day_yield
    if df.iloc[index]['Two_day_yield'] == "Down":
        res += "0"
    elif df.iloc[index]['Two_day_yield'] == "Up":
        res += "1"
    else:  # Equal
        res += "2"
    # Three_day_yield
    if df.iloc[index]['Three_day_yield'] == "Down":
        res += "0"
    elif df.iloc[index]['Three_day_yield'] == "Up":
        res += "1"
    else:  # Equal
        res += "2"
    return res


# Create situation bank
situation_bank = []
for a in range(3):
    for b in range(3):
        for c in range(3):
            for d in range(3):
                for e in range(3):
                    num = (str(a) + str(b) + str(c) + str(d) + str(e))
                    situation_bank.append(num)
long_situation_bank = [i for i in situation_bank]
short_situation_bank = []

# Randomise the decisions
change_to_short_set = set()
while len(change_to_short_set) < 100:
    change_to_short_set.add(random.randint(0, 242))
change_to_out_set = set()
while len(change_to_out_set) < 15:
    num = random.randint(0, 242)
    if num not in change_to_short_set:
        change_to_out_set.add(num)

for i in change_to_short_set:
    num = situation_bank[i]
    long_situation_bank.remove(num)
    short_situation_bank.append(num)
for i in change_to_out_set:
    num = situation_bank[i]
    long_situation_bank.remove(num)

# Determine when we go long, short and out
for i in list(experiment_df.index.values):
    situation = Identifier(i, rates_experiment_df, experiment_df)
    if situation in long_situation_bank:
        long_index_list.append(i)
    elif situation in short_situation_bank:
        short_index_list.append(i)

# Test
# print(Market_Action(long_index_list,
# short_index_list,
# experiment_df.index.values,
# experiment_df,
# economic_dataframe,
# start_sum = 10000))
