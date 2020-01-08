Pre-requisite:
For the script to run successfully, you would need Python 2.7 running on the server as well as python-pip and pycurl package. You can install pycurl using the following command: sudo apt install python-pycurl and pip using: apt-get python-pip. 
Next steps:
It contains the packages that will be required for the python script to run successfully. To install these packages, run “source Install_dependencies.txt” and it would install the required libraries.

Details of the script package:

1.	Config.json
Tenant-details
-	Tenant-URL: URL of the tenant
-	API-GET Token: API Token that will be used to fetch the data using USQL.
-	API-POST Token: API Token with Post/Config permission which will be used to create “Custom Device” and publish “timeSeries” metrics to the custom device.

Application-details:
-	app-name: app name which will be used to name and create the custom device. It is recommended to be the application name for which you would be running the USQL queries on.
-	use-case:
o	api: definition of the USQL query which will be executed using the script.
o	displayname: The display name on UI to display the value fetched by the respective api.
o	timeseriesId: timeseriesId which will be used to store the data internally for the api values. Please note the name should have the prefix custom: always.
Log file
-	the log file that would be generated to store the logs for the python script.

2.	Usql_restore.py
This is a python script that would execute to fetch the records every 2 hours using the API-GET Token. To fetch the records, script would use USQL queries for the past 2 hours. Once these records are fetched, it would push back the metrics as custom metrics to the custom device created for those use-cases.

3.	Constant.py
It is a constant which will be used by the script to populate/push records in the database.

Known limitations:
1.	The custom device created through API (in this case the script) cannot be manually deleted. It would fade away once the data injection stops for that device.
2.	Custom Metrics fed back to custom device (through the script) cannot be older than past 1 hour. This is a known functionality for custom device and custom timeseries metrics. 
So in essence if the script is turned off for say 2 hours, then the data generated for the 1st 1-hour window would be lost and there is no way that the data can be pumped back in.
3.	Each use-case will lead to defining a new “custom metric” and lead to custom metrics consumptions. SIA currently has 1.5k custom metrics available to be consumed.
4.	Currently the script is designed to pull count metrics like count(users) which performed a particular action, etc.

To run the script, execute “python -u usql_restore.py”
