import csv
import xlsxwriter as xlw
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
from io import StringIO
from pathlib import Path
import os

working_directory = os.path.abspath('')
header = []; dates = []; tx = []; newsaleslist = []; ATMtotals = []; DailyTotals = []; DailyVolume = []; salesSub1000 = []; ZeroTX = []; Sales1000Daily = [] # salesSub200 = [];
total = 0; i = 0; #avg = 0;
lastDate = ''; lastATM =''
Append = False

#Get my Header & Rows
sales = open(working_directory+'/Sales/Monthly - CSVs/TEST_DATA_SALES.csv',"r")
for rows in sales:
    if i == 0:
        i +=1
        header = rows.split(',')
    else:
        tx.append(rows.split(','))
sales.close()

#rename header from CAD to Daily total
header[11]="Daily total"

#Append the rows to the new sales list
i = 0
for t in tx:
    newsaleslist.append([str(tx[i][0])[0:10],tx[i][1],tx[i][11]])
    i += 1

#Sort the new sales list by name
newsaleslist.sort(key=lambda x: x[1])

#change the cash to int
for t in range(len(newsaleslist)):
    newsaleslist[t][2] =int(newsaleslist[t][2])

#make lists from the data. Volume (#tx), Total sales, Sales under 1000, sales under 200, # of 0 tx's
DailyTotals.append([newsaleslist[0][0],0]); DailyVolume.append([newsaleslist[0][0],0]); salesSub1000.append([newsaleslist[0][0],0]); Sales1000Daily.append([newsaleslist[0][0],0]);ZeroTX.append([newsaleslist[0][0],0])

for L in newsaleslist:
    #daily cash totals list building
    for D in DailyTotals:
        Append = True
        if L[0] in D:
            DailyTotals[DailyTotals.index(D)][1] = DailyTotals[DailyTotals.index(D)][1]+L[2]
            Append = False
            break
    if Append == True:
        DailyTotals.append([L[0],L[2]])
    #daily volume of sales count list building
    for V in DailyVolume:
        Append = True
        if L[0] in V:
            if L[2] != 0:
                DailyVolume[DailyVolume.index(V)][1] +=1 #DailyVolume[DailyVolume.index(V)][1]+1
            Append = False
            break
    if Append == True:
        if L[2] != 0:
            DailyVolume.append([L[0],1])
        else:
            DailyVolume.append([L[0],0])
    #daily volume of sales unser 1,000.00CAD list building
    for S1 in salesSub1000:
        Append = True
        if L[0] in S1:
            if L[2] < 1000 and L[2] != 0:
                salesSub1000[salesSub1000.index(S1)][1] +=1 #salesSub1000[salesSub1000.index(V)][1]+1
            Append = False
            break
    if Append == True:
        if L[2] < 1000 and L[2] != 0:
            salesSub1000.append([L[0],1])
        else:
            salesSub1000.append([L[0],0])
#daily total of sales unser 1,000.00CAD list building
    for S1D in Sales1000Daily:
        Append = True
        if L[0] in S1D:
            if L[2] < 1000 and L[2] != 0:
                Sales1000Daily[Sales1000Daily.index(S1D)][1] += L[2]
            Append = False
            break
    if Append == True:
        if L[2] < 1000 and L[2] != 0:
            Sales1000Daily.append([L[0],L[2]])
        else:
            Sales1000Daily.append([L[0],0])

    #daily volume of sales = 0.00CAD list building
    for S0 in ZeroTX:
        Append = True
        if L[0] in S0:
            if L[2] == 0:
                ZeroTX[ZeroTX.index(S0)][1] +=1 #ZeroTX[ZeroTX.index(V)][1]+1
            Append = False
            break
    if Append == True:
        if L[2] == 0:
            ZeroTX.append([L[0],1])
        else:
            ZeroTX.append([L[0],0])

#sort the lists by date
DailyTotals.sort(key=lambda x: x[0])
DailyVolume.sort(key=lambda x: x[0])
salesSub1000.sort(key=lambda x: x[0])
Sales1000Daily.sort(key=lambda x: x[0])
# salesSub200.sort(key=lambda x: x[0])
ZeroTX.sort(key=lambda x: x[0])

#drop the dates from each list so that its just a list of numbers not a list of lists
for D in DailyTotals:
    DailyTotals[DailyTotals.index(D)] = D[1]
for V in DailyVolume:
    DailyVolume[DailyVolume.index(V)] = V[1]
for S1 in salesSub1000:
    salesSub1000[salesSub1000.index(S1)] = S1[1]
for S1D in Sales1000Daily:
    Sales1000Daily[Sales1000Daily.index(S1D)] = S1D[1]
for S0 in ZeroTX:
    ZeroTX[ZeroTX.index(S0)] = S0[1]

#Calculate the daily total for each ATM and delete extra days as you do it
i = 0
for t in range(len(newsaleslist)+1):
    if i == len(newsaleslist):
        newsaleslist[i-1][2] = float(newsaleslist[i-1][2])
        break
    #this case sets the initial values
    if lastDate != newsaleslist [i][0] and total == 0:
       lastDate = newsaleslist[i][0]
       total = int(newsaleslist[i][2])
       #avg = 1 
    #this case adds to the denominator & numerator and also deletes the previous entry      
    elif lastDate == newsaleslist [i][0] and total != 0:
        lastDate = newsaleslist[i][0]
        total += int(newsaleslist[i][2])
        #avg += 1
        del newsaleslist[i-1]
        i -= 1
    #this case wraps up a daily total and resets the numerator and denominator
    elif lastDate != newsaleslist [i][0] and total != 0:
        lastDate = newsaleslist[i][0]
        newsaleslist[i-1][2] = total#/avg
        total = int(newsaleslist[i][2])
        #avg = 1
    i += 1

#create the header for the xlsx file (grid)
headings = ['Date']
for k in range(len(newsaleslist)):
    if newsaleslist[k][1] not in headings:
        headings.append(newsaleslist[k][1])
#create the list of dates
for k in range(len(newsaleslist)):
    if newsaleslist[k][0] not in dates:
        dates.append(newsaleslist[k][0])
dates.sort()

# we will now make the work book and write each series(atm location) into the 
# sheet as the header row, and each date as a row 'header'
workbook = xlw.Workbook(working_directory+'/Sales/DATA TABLES/SAMPLE_DATA_TABLE.xlsx')
worksheet = workbook.add_worksheet('all locations data')
bold = workbook.add_format({'bold': True})
worksheet.write_row(0,0, headings, bold)
worksheet.write_column(1,0, dates, bold)

#populate the rest of the fields
for k in range(len(newsaleslist)):
    cl = headings.index(str(newsaleslist[k][1]))
    rw = dates.index(str(newsaleslist[k][0]))
    worksheet.write(rw+1,cl,newsaleslist[k][2])

#Write the totals row
total = 0
lastATM = newsaleslist[0][1]
for k in range(len(newsaleslist)):
    if lastATM == newsaleslist[k][1]:
        lastATM = newsaleslist[k][1]    
        total += newsaleslist[k][2]
    else:
        lastATM = newsaleslist[k][1] 
        ATMtotals.append(total)
        total = newsaleslist[k][2]
ATMtotals.append(total)

#add the special lists we want to see like total cash per day, volume per day, volume under 1k per day, total cash of tx under 1k per day, 0 tx per day
worksheet.write(0,len(headings),"Total Cash",bold)           
worksheet.write(len(dates)+1,0,"Total Cash",bold)
worksheet.write_column(1,len(headings),DailyTotals,bold)   
worksheet.write_row(len(dates)+1,1,ATMtotals,bold)
worksheet.write(0,len(headings)+1,"Volume",bold)
worksheet.write(0,len(headings)+2,"TX < 1000 vol",bold)
worksheet.write(0,len(headings)+3,"TX < 1000 totals/day",bold) 
# worksheet.write(0,len(headings)+3,"TX < 200",bold)       
worksheet.write(0,len(headings)+4,"ZERO TX",bold)   
worksheet.write_column(1,len(headings)+1,DailyVolume,bold)     
worksheet.write_column(1,len(headings)+2,salesSub1000,bold)
worksheet.write_column(1,len(headings)+3,Sales1000Daily,bold)  
# worksheet.write_column(1,len(headings)+3,salesSub200,bold) 
worksheet.write_column(1,len(headings)+4,ZeroTX,bold) 
workbook.close()
