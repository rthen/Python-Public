import requests
import sys
import subprocess
import json

api_key = "[API_KEY]"
rapid7_api_v1 = "https://us.api.insight.rapid7.com/idr/v1"
rapid7_api_v2 = "https://us.api.insight.rapid7.com/idr/v2"

def list_investigations():
    investigations_endpoint = rapid7_api_v2 + "/investigations"
    params = {'statuses': 'OPEN', "priorities": "LOW", "source": "ALERT"} 
    headers = {"X-Api-Key": api_key, "Accept-version": "investigations-preview"}

    response = requests.get(investigations_endpoint, headers=headers, params=params)
    requests_results = response.json()

    leaked_investigations_rrn = []

    if (response.status_code) == 200:
        investigations_data = requests_results.get("data")
        if investigations_data:
            for investigation in investigations_data:
                # Retrieve rrn of investigations that matches leak related alerts
                if ( "leaked" in investigation["title"] ):
                    investigation_rrn = investigation["rrn"]
                    leaked_investigations_rrn.append(investigation_rrn)
        else:
            print("No investigations found. Terminating script...")
            sys.exit(1)
    else:
        print(f"Request failed with status code {response.status_code}")
        sys.exit(1)
        
    return leaked_investigations_rrn

def get_investigation_evidence(investigations):
    leaked_accounts = {}

    for investigation_rrn in investigations:
        investigations_evidence_endpoint = rapid7_api_v1 + "/restricted/investigations/" + investigation_rrn + "/evidence"
        params = {'statuses': 'OPEN'} 
        headers = {"X-Api-Key": api_key, "Accept-version": "investigations-preview"}
        
        response = requests.get(investigations_evidence_endpoint, headers=headers, params=params)
        requests_results = response.json()
        
        indicator_occurrences = requests_results["indicator_occurrences"]

        for entry in indicator_occurrences:
            evidences = entry["evidence"]
            for evidence in evidences:
                account_name = (evidence["details"]).get("account")

                if account_name:
                    """
                    Rapid7 evidence API can return duplicate email addresses since the attribute 'name' 
                    appears multiple times on the response. To get around this, the set data type is used 
                    for values while using the investigation ID as a key. 
                    """
                    username = account_name["name"]
                    try:
                        leaked_accounts[investigation_rrn].add(username)
                    except:
                        leaked_accounts[investigation_rrn] = {username}
           
    return leaked_accounts

def update_investigation(ad_status, rrn):
    investigations_comment_endpoint = rapid7_api_v1 + "/comments"
    payload = json.dumps({
        "target": rrn,
        "body": ad_status
    })
    headers = {"X-Api-Key": api_key, "Accept-version": "comments-preview", 'Content-Type': 'application/json'}
    
    response = requests.post(investigations_comment_endpoint, headers=headers, data=payload)
    print(ad_status, rrn)

def check_ad_acct_status(leaked_users):
    # Import AD module if found, otherwise, error is thrown
    import_ad_module_commmand = "Import-Module ActiveDirectory"
    import_ad_module_process = subprocess.Popen(["powershell", import_ad_module_commmand], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    import_ad_module_output, import_ad_module_error = import_ad_module_process.communicate()
    import_ad_module_return_code = import_ad_module_process.returncode

    if import_ad_module_return_code == 0:
        print("AD module successfully imported")
    else:
        print("Unable to import AD module. Terminating script. Error code: ", import_ad_module_return_code)
        print("Error:\n", import_ad_module_error.decode("utf-8"))
        sys.exit(1)

    # Check if the account exists within local AD, if so, retrieved the DN (or any attribute that is useful)
    for rrn, email_addresses in leaked_users.items():
        for email in email_addresses:
            username = email.split("@")[0]

            get_aduser_command = f"(Get-ADUser -Identity {username} -Properties DistinguishedName).DistinguishedName"
            get_aduser_process = subprocess.Popen(["powershell", get_aduser_command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            get_aduser_output, get_aduser_error = get_aduser_process.communicate()
            get_aduser_return_code = get_aduser_process.returncode
            get_aduser_error_decoded = get_aduser_error.decode("utf-8")
            
            if get_aduser_return_code == 0:
                distinguishedname = get_aduser_output.decode("utf-8")
                ad_status = f"{username} exists in AD. DN: {distinguishedname}"
                update_investigation(ad_status, rrn)

            elif "Get-ADUser : Cannot find an object with identity:" in get_aduser_error_decoded:
                ad_status =  f"{username} does not exists in AD"
                update_investigation(ad_status, rrn)
            else:
                print("PowerShell command failed with the following error code: ", get_aduser_return_code)
                print("Error: ", get_aduser_error_decoded)

leaked_investigations_rrn = list_investigations()
leaked_users = get_investigation_evidence(leaked_investigations_rrn)
check_ad_acct_status(leaked_users)
