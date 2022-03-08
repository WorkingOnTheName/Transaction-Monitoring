import pandas as pd
import datetime as dt
from csv import writer
from pathlib import Path
import os

working_directory = os.path.abspath('')

rule1New=pd.DataFrame(); rule2New=pd.DataFrame(); rule3New=pd.DataFrame(); rule1YearAgo=pd.DataFrame(); rule2YearAgo=pd.DataFrame(); rule3YearAgo=pd.DataFrame();
highrisk=pd.DataFrame({'Strike Score':None,'Risk': None,'Day Deemed High Risk':None,}, index=pd.Index([None],name='Customer ID'))
no_duplicate_list = []
CustomerStrikeCounter = {}
today = dt.date.today(); YearAgo = pd.to_datetime(dt.date(today.year-1,today.month,today.day)); NextYear = pd.to_datetime(dt.date(today.year+1,today.month,today.day))

#CSV Functions
def append_a_line(file_name,sentance):
    with open(file_name,'a', newline='') as write_obj:
        csv_writer = writer(write_obj)
        csv_writer.writerow(sentance)
def clean_a_csv(file_name):
    open(file_name,'w', newline='')
def no_duplicate_rows(file_name):
    df = pd.read_csv(file_name)
    df.drop_duplicates(inplace=True)
    df.to_csv(file_name,mode='w+',index=False,header=True)
def import_past_year(file_name,df_to_fill):
    df_to_fill = pd.read_csv(file_name,index_col=0)
    df_to_fill.index = pd.to_datetime(df_to_fill.index)
    df_to_fill = df_to_fill[df_to_fill.index[:]>YearAgo]
    return df_to_fill

#cleaning the current flag files
clean_a_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR1.csv')
clean_a_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR2.csv')
clean_a_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR3.csv')
#importing historical data (we have already risk scored)
OldData = pd.read_csv(working_directory+'/HighRisk/riskscorefiles/History.csv', index_col=0)
OldData.index = pd.to_datetime(OldData.index )
#importing the new data we want to add to our old risk score data
ImportedData = pd.read_csv(working_directory+'/HighRisk/riskscorefiles/Randomized_Sample_Data.csv', usecols=["Date","Invoice","Customer","Cash"])
#ImportedData = ImportedData.loc[:,["Date","Invoice","Customer","Cash"]]
ImportedData.set_index("Date", inplace=True)
ImportedData.index = pd.to_datetime(ImportedData.index)
ImportedData.index = ImportedData.index.normalize()

#filtering out the new transactions from the ones that we may have already checked. 
#for example we could accidentally import some old (already flagged/vetted) transactions.
MergedData = pd.merge(ImportedData, OldData, how='inner')
NewData = pd.concat([ImportedData,MergedData]).drop_duplicates(keep=False)
NewData.index.set_names('Date',inplace=True)
#NewData["Customer"].fillna(0, inplace=True)
NewData.to_csv(working_directory+'/HighRisk/riskscorefiles/History.csv', mode='a', index=True, header=False)
no_duplicate_rows(working_directory+'/HighRisk/riskscorefiles/History.csv')
#if there is no new transactions to consider quit the script
if NewData.size == 0:
    quit()

#Generating Rule 1 & dropping them from the new data
for date, customer in list(set(zip(NewData.index,NewData.Customer))):
    day = NewData[(NewData.index==date)&(NewData.Customer==customer)]
    DailyTotal = sum(day.Cash)
    if DailyTotal>=10000:
        rule1New = rule1New.append(day)
NewData = pd.concat([NewData,rule1New]).drop_duplicates(keep=False)

#Generate Rule 2; drop nothing from the new data
rule2New = NewData.loc[NewData.loc[:,'Cash'].between(8000,9995, inclusive='both')]

#Generating Rule 3; drop nothing from the new data
[no_duplicate_list.append(x) for x in list(set(zip(NewData.index.month_name(),NewData.Customer))) if x not in no_duplicate_list]
for CurrentMonth, customer in no_duplicate_list:
    Month = NewData[(NewData.index.month_name()==CurrentMonth)&(NewData.Customer==customer)]
    MonthlyTotal = sum(Month.Cash)
    if MonthlyTotal>=25000:
        rule3New = rule3New.append(Month)

#Updating the Flagged History File with the new batch of flags from this run
rule1New.to_csv(working_directory+'/HighRisk/riskscorefiles/Rule1History.csv', mode='a', index=True, header=False)
rule2New.to_csv(working_directory+'/HighRisk/riskscorefiles/Rule2History.csv', mode='a', index=True, header=False)
rule3New.to_csv(working_directory+'/HighRisk/riskscorefiles/Rule3History.csv', mode='a', index=True, header=False)
#removing duplicates from History Files
no_duplicate_rows(working_directory+'/HighRisk/riskscorefiles/Rule1History.csv')
no_duplicate_rows(working_directory+'/HighRisk/riskscorefiles/Rule2History.csv')
no_duplicate_rows(working_directory+'/HighRisk/riskscorefiles/Rule3History.csv')
#Creating the list of flags from this run to be inspected/reported/whatever
rule1New.to_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR1.csv', mode='a', index=True, header=True)
rule2New.to_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR2.csv', mode='a', index=True, header=True)
rule3New.to_csv(working_directory+'/HighRisk/riskscorefiles/FlaggedNowR3.csv', mode='a', index=True, header=True)

#Time to import the history of flagged transactions, look back 1 year, and start scoring customers
rule1YearAgo = import_past_year(working_directory+'/HighRisk/riskscorefiles/Rule1History.csv',rule1YearAgo)
rule2YearAgo = import_past_year(working_directory+'/HighRisk/riskscorefiles/Rule2History.csv',rule2YearAgo)
rule3YearAgo = import_past_year(working_directory+'/HighRisk/riskscorefiles/Rule3History.csv',rule3YearAgo)

#counting the strikes...3 strikes you're out (high risk)
for day, customer in list(set(zip(rule1YearAgo.index, rule1YearAgo.Customer))):
    if customer not in CustomerStrikeCounter:
        CustomerStrikeCounter[customer] = 1
    else:
        CustomerStrikeCounter[customer] += 1
for customer in list(rule2YearAgo.Customer):
    if customer not in CustomerStrikeCounter:
        CustomerStrikeCounter[customer] = 1
    else:
        CustomerStrikeCounter[customer] += 1
for Month, customer in list(set(zip(rule3YearAgo.index.month_name(), rule3YearAgo.Customer))):
    if customer not in CustomerStrikeCounter:
        CustomerStrikeCounter[customer] = 1
    else:
        CustomerStrikeCounter[customer] += 1

#Using the strike score dictionary to add/update the highrisk/lowrisk dataframe
for customer in CustomerStrikeCounter:
    if CustomerStrikeCounter[customer] > 2 and customer not in highrisk.index:
        highrisk = pd.concat([(pd.DataFrame({'Strike Score':CustomerStrikeCounter[customer],'Risk': 'High','Day Deemed High Risk':today}, index=pd.Index([customer],name='Customer ID'))),highrisk])
    elif CustomerStrikeCounter[customer] < 3 and customer not in highrisk.index:
        highrisk = pd.concat([(pd.DataFrame({'Strike Score':CustomerStrikeCounter[customer],'Risk': 'Low','Day Deemed High Risk':'N/A'}, index=pd.Index([customer],name='Customer ID'))),highrisk])
    elif CustomerStrikeCounter[customer] > 2 and customer in highrisk.index:
        highrisk.loc[[customer]]=pd.DataFrame({'Strike Score':CustomerStrikeCounter[customer],'Risk': 'High','Day Deemed High Risk':today}, index=pd.Index([customer],name='Customer ID'))
    elif CustomerStrikeCounter[customer] < 3 and customer in highrisk.index:
        highrisk.loc[[customer]]=pd.DataFrame({'Strike Score':CustomerStrikeCounter[customer],'Risk': 'Low','Day Deemed High Risk':'N/A'}, index=pd.Index([customer],name='Customer ID'))

#Sending the highrisk dataframe to a csv
clean_a_csv(working_directory+'/HighRisk/riskscorefiles/HighRisk.csv')
highrisk.to_csv(working_directory+'/HighRisk/riskscorefiles/HighRisk.csv', mode='a', index=True, header=True)