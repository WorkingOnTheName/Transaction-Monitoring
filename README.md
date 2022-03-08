# Transaction-Monitoring
Automated transaction monitoring with pandas

Sales is a stand alone script that takes the raw sales data for any period of time, and creates a table that shows various metrics for each locations performance for the given period of time.The table also shows the total across all locations per day, transaction volume per day, how many transactions were less than & greater than 1000, and how many were zero transacions.

The High Risk script is also a stand alone script which can read the same raw sales data for any period of time, and flag certain transactons based on preset rules. Aditionally this script will score customers based on how risky they are (according to thier transactions). 

The Unusual Transaction script depends on the results of the High Risk script. This script takes the flagged transactions and populates log with preset fields depending on the type of transaction being pushed into the log. 
