# -PyIntelX (IntelligenceX for Bug Bounty) - IntelX
I'm designed to search and extract credentials from the IntelX API, just enter the target domain to me.

Sample Slack Logs with Bug bounty target credential leaks
<img width="712" alt="POC" src="https://github.com/sherlocksecurity/PyIntelX/assets/52328067/40095eb0-b7dc-473d-aa31-e11315e66f4c">



IntelligenceX is a powerful tool that is designed to collect all bot logs from compromised employees of various organizations. This tool can be used to find valuable information such as employee credentials (Like Github Leaks), by simply providing the relevant keywords. With its advanced scanning capabilities, PyIntelX can help you quickly identify the orgs leaks.

More info: https://intelx.io/about

# Requirements
* Intelligences Professional/Researcher License (https://intelx.io/order)
* A Slack Channel & Slack Bot with write,upload,read permissions
* Environment Variables 

```IntelX_API_KEY``` API Key for IntelX API
```Slack_Bot_Token``` Bot token for Slack API
```Slack_Channel``` Slack channel where results will be posted

# Installation

* Install dependencies ```pip3 install -r requirements.txt```
* Set the environment variables (Eg: ```export INTEL_API_KEY="YOURKEYHERE"```)
*  ```export Slack_Bot_Token=Bot Token```
*  ```export Slack_Channel=ChannelID```
* Create all the files if not created by script (search_ids.txt and storage_ids.txt) with no content inside. 
* Run the script ```python3 PyIntelX.py```

#You can configure the script to run on cronjob everyday, intelx update their dataset every 24hrs

