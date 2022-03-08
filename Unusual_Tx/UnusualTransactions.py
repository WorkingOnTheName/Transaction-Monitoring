import pandas as pd
import datetime as dt
from csv import writer
from pathlib import Path
import os

working_directory = os.path.abspath('')
today = dt.date.today(); YearAgo = pd.to_datetime(dt.date(today.year-1,today.month,today.day))

def clean_a_csv(file_name):
    open(file_name,'w', newline='')

unusualLog = pd.read_csv(working_directory+'/Unusual_Tx/UnusualFiles/Unusual_Transaction_Log.csv', index_col=0)
LargeCash = pd.read_csv(working_directory+'/HighRisk/riskscorefiles/Rule1History.csv', index_col=1)
unusualTransactions = pd.read_csv(working_directory+'/HighRisk/riskscorefiles/Rule2History.csv', index_col=1)

LargeCash.index.rename('Transaction Identifier', inplace=True)
LargeCash.insert(0,'Date of Discovery', today)
LargeCash.insert(1,'Discovery Method (Staff, Sales Agent, System Alert)', 'System Alert')
LargeCash.insert(2,'Compliance Reviewer', 'Eissa')
LargeCash.insert(3,'Transaction Description', 'Large Cash')
LargeCash.insert(4,'Was the transaction completed?', 'yes')
LargeCash.insert(5,'Is the transaction suspicious?', 'yes')
LargeCash.insert(6,'Why was the transaction considered to be suspicious OR considered not to be suspicious?', 'Customer purchased greater than $10,000.00 CAD in one calendar day.')
LargeCash.insert(7,'FINTRAC Report Number', '')
LargeCash.insert(8,'Date that the transaction was deemed to be suspicious', today)
LargeCash.insert(9,'FINTRAC Reporting Date', '')
LargeCash.insert(10,'Follow-up Activity', 'None')
LargeCash = LargeCash[['Date of Discovery','Discovery Method (Staff, Sales Agent, System Alert)','Compliance Reviewer','Transaction Description','Was the transaction completed?','Is the transaction suspicious?','Why was the transaction considered to be suspicious OR considered not to be suspicious?','FINTRAC Report Number','Date that the transaction was deemed to be suspicious','FINTRAC Reporting Date','Follow-up Activity','Customer','Cash','Date']]
LargeCash.rename(columns={'Customer':'Customer #','Cash':'CAD' ,'Date':'tx date'}, inplace=True)

unusualTransactions.index.rename('Transaction Identifier', inplace=True)
unusualTransactions.insert(0,'Date of Discovery', today)
unusualTransactions.insert(1,'Discovery Method (Staff, Sales Agent, System Alert)', 'System Alert')
unusualTransactions.insert(2,'Compliance Reviewer', 'Eissa')
unusualTransactions.insert(3,'Transaction Description', 'Structuring(<10k)')
unusualTransactions.insert(4,'Was the transaction completed?', 'yes')
unusualTransactions.insert(5,'Is the transaction suspicious?', 'no')
unusualTransactions.insert(6,'Why was the transaction considered to be suspicious OR considered not to be suspicious?', 'This transaction may be part of a structured payment; however is not reportable. This transaction is unusual since it is large, but not reportable since it is below 10k in one calendar day.')
unusualTransactions.insert(7,'FINTRAC Report Number', '')
unusualTransactions.insert(8,'Date that the transaction was deemed to be suspicious', 'N/A')
unusualTransactions.insert(9,'FINTRAC Reporting Date', '')
unusualTransactions.insert(10,'Follow-up Activity', '')
unusualTransactions = unusualTransactions[['Date of Discovery','Discovery Method (Staff, Sales Agent, System Alert)','Compliance Reviewer','Transaction Description','Was the transaction completed?','Is the transaction suspicious?','Why was the transaction considered to be suspicious OR considered not to be suspicious?','FINTRAC Report Number','Date that the transaction was deemed to be suspicious','FINTRAC Reporting Date','Follow-up Activity','Customer','Cash','Date']]
unusualTransactions.rename(columns={'Customer':'Customer #','Cash':'CAD' ,'Date':'tx date'}, inplace=True)

#how to make sure there are no duplicates in the log
for i in LargeCash.index:
    if i not in unusualLog.index:
        unusualLog = unusualLog.append(LargeCash.loc[i])

for j in unusualTransactions.index:
    if j not in unusualLog.index:
        unusualLog = unusualLog.append(unusualTransactions.loc[j])

clean_a_csv(working_directory+'/Unusual_Tx/UnusualFiles/NewUnusualTxLog.csv')
unusualLog.to_csv(working_directory+'/Unusual_Tx/UnusualFiles/NewUnusualTxLog.csv', mode='a', index=True, header=True)