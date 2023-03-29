# ----------PyIntelX (Draft) --Will update with more detailed version -----------
I'm designed to search and extract data from the IntelX API using specific keywords provided in the ```keywords.py``` file.

The data is then processed to find any passwords files and reports the results to a Slack channel using the Slack API.

# Environment Variables
The following environment variables are required to be set:

```IntelX_API_KEY``` API Key for IntelX API
```Slack_Bot_Token``` Bot token for Slack API
```Slack_Channel``` Slack channel where results will be posted

# How to run
To run the script:

* run ```git clone git@github.com:sherlocksecurity/PyIntelX.git```
* Install dependencies ```pip3 install -r requirements.txt```
* Set the environment variables (Eg: ```export INTEL_API_KEY="YOURKEYHERE"```)
* Run the script ```python3 PyIntelX.py```

# Description of files
* ```PyIntelX.py``` The main Python script file that searches and extracts data from IntelX API using the keywords and reports the results to Slack channel.

* ```keywords.py``` The file contains the list of keywords to search for.

* ```search_ids.txt``` The file stores the search ID of the latest search.

# Flow

* Import required libraries and modules.

* Set up environment variables and parameters for the IntelX API search.

* Define the ```search()``` function that performs a search for a specific keyword.
* Define the ```get_result()``` function that gets the search results for a specific search ID.
* Define the ```process_results()``` function that processes the search results and reports the password files found in Slack channel.
* Main script to execute the search and process the results. The script reads the list of keywords from keywords.py and performs a search for each keyword using the search() function. The search results are then processed using the process_results() function to look for password files. If any password files are found, the results are reported to the Slack channel using the Slack API.

# Notes
* The SSL certificate verification is disabled by setting the ```_create_unverified_context()``` function of the SSL library.
* The ```search_ids.txt``` file is created if it doesn't exist, and stores the search ID of the latest search. The search ID is used to get the search results for a specific search. If the file exists, the search ID is read from the file to get the search results.
* If there are no search results for a specific search, the script skips the keyword and moves on to the next keyword.
