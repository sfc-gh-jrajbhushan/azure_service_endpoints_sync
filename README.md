# azure_service_endpoints_sync
# Project Title
Automate syncing your Snowflake Network Policy with the Azure Weekly Service Tag Refresh 

## Description
Microsoft Azure publishes IP address ranges for their services (PowerBI, Storage, SQL, AzureTrafficManager, etc). The ranges are available as part of a JSON file and are updated weekly. They recommend downloading the file every week and appropriately whitelisting the IP ranges here's an excerpt from the download page: 

   "Please download the new json file every week and perform the necessary changes at your site to correctly identify services running in Azure"

Given that there are frequent changes, customers using azure services (PowerBI, etc) run into connectivity issues since the new IPs need to be added to the Network Policy's allow_list. Keeping the IPs in sync is a painful exercise. This code automates the process:

   1. Download the json file 
   2. Load the IP Addresses to a Snowflake table
   3. Fetch only the missing/newly added IPs,
   4. Return an "alter network policy" statement with the latest IPs appended to the network policy
      **This doesn't handle IPs that are removed in the most recent file 

# Note: 
Below is the URL where the file can be downloaded along with the description on why this needs to be done. 

https://www.microsoft.com/en-us/download/details.aspx?id=56519

# Text from the page: 
 IP address ranges for Public Azure as a whole, each Azure region within Public, and ranges for several Azure Services (Service Tags) such as Storage, SQL and AzureTrafficManager in Public. This file currently includes only IPv4 address ranges but a schema extension in the near future will enable us to support IPv6 address ranges as well. Service Tags are each expressed as one set of cloud-wide ranges and broken out by region within that cloud. This file is updated weekly. New ranges appearing in the file will not be used in Azure for at least one week. Please download the new json file every week and perform the necessary changes at your site to correctly identify services running in Azure. These service tags can also be used to simplify the Network Security Group rules for your Azure deployments though some service tags might not be available in all clouds and regions. Customers viewing the Effective Security Rules for their network adapters may note the presence of the “special” Azure platform addresses ( 168.63.129.16, FE80::1234:5678:9ABC/128) which are part of the Azure platform and NOT included in the JSON files. These platform addresses are described in more detail here: https://docs.microsoft.com/en-us/azure/virtual-network/what-is-ip-address-168-63-129-16. For more information on Service Tags please visit http://aka.ms/servicetags.


## Setup

1. unzip the folder
2. create a new conda environment (conda create --name <new env>)
3. conda activate <new env>
4. Run the statement: pip3 install --upgrade -r requirements.txt
5. Edit the config.yaml file (substitute credentials, account, db, schema, etc)
6. navigate to src folder and run: main.py 
7. logon to the snowflake account, run the below query, which should return three main columns: IPs in the current NW policy, new IPs from the Azure file, Alter network policy statement
    select * 
      from <db>.<schema>.azureiplist_core;

