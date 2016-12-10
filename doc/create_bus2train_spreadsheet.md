# How to Make Bus and Trains per Hour Spreadsheet

## SQL

* To get all the buses hours near train stations run [bus SQL](/postgres/bus2train/all_buses_near_train_stations.sql).
* To get all the train hours run [train SQL](/postgres/bus2train/all_trains_hours.sql).
* Export query result to csv/excel.
* Make sure the result sheet is named result (re:dash does it automatically).


## Create the Excel

* Open the csv/excel with excel (bus and train).
* Add to the result sheet "total weekdays operating" column and paste this formulas: =COUNTIF(G2:K2,"TRUE") to the column.
* In every file add 3 sheets: bus_weekday, bus_friday, bus_saturday and train_weekday, train_friday, train_saturday.
* Copy the sheets with the formulas from these two files: [train table](https://drive.google.com/open?id=0B9FEqRIWfmxLSm9VNkFYOWVtdzg) and [bus table](https://drive.google.com/open?id=0B9FEqRIWfmxLMjVfc1hBQ0hWbWs).
* Please note if you copy the result sheet to another file it will probably get stuck. This is why you need to copy the formulas instead.
* When you copy a sheet from one workbook to another it adds the name of the workbook. use find & replace to erase it from your workbook.

almost there....:muscle:

* Copy all six sheets to the following  [file](https://drive.google.com/open?id=0B9FEqRIWfmxLX0FxaG9pdE1iVWM). Paste the sheet without the formulas.(use special paste - Values and Source Formatting)
* Update the readme and you're done!
