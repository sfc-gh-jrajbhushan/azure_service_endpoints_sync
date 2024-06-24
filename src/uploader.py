# src/uploader.py
import os
from pathlib import Path
import snowflake.connector
import logging
import regex as re
from datetime import datetime


def setup_snowflake_conn(config):
    logger = logging.getLogger()
    logger.info("uploader.py: setup_snowflake_conn()")        
    try:

        sf_account = config['account']
        sf_username = config['user_name']
        sf_password = config['password']
        sf_database = config['database_name']
        sf_schema = config['schema_name']
        sf_role = config['role_name']
        sf_warehouse = config['warehouse_name']

        connection_params = {
        'account': sf_account,
        'user': sf_username,
        'password': sf_password,
        'database': sf_database,
        'schema': sf_schema,
        'role': sf_role,
        'warehouse': sf_warehouse
        }

        conn = snowflake.connector.connect(**connection_params)
        cur = conn.cursor()
        logger.info(f"Connection successful")
        return cur
    
    except snowflake.connector.errors.Error as e:
        logger.error(f"Failed to establish a connection:", exc_info=True)
        raise


def find_latest_file(file_path):

    logger = logging.getLogger()
    logger.info("uploader.py: find_latest_file()")

    # Regular expression to extract date from filenames (assuming YYYYMMDD format)
    date_pattern = re.compile(r'\d{8}')

    most_recent_date = None
    most_recent_file = None

    for filename in os.listdir(file_path):
        # Search for the date in the filename
        match = date_pattern.search(filename)
        if match:
            file_date_str = match.group()
            # Parse the date
            file_date = datetime.strptime(file_date_str, '%Y%m%d')
            # Compare dates
            if most_recent_date is None or file_date > most_recent_date:
                most_recent_date = file_date
                most_recent_file = filename

    return most_recent_file



def validate_and_load(config, cur, file_path, file_name):

    logger = logging.getLogger()
    logger.info("uploader.py: validate_and_load()")        

    database_name = config['database_name']
    schema_name = config['schema_name']
    stage_name = config['stage_name']
    network_policy = config['network_policy']

    try:
        cur.execute("select current_version()")
        ver = cur.fetchall()

        logger.info(f"file_path: {file_path}")
        #Upload the file to an internal stage, overwrite the file if it already exists:
        cur.execute("PUT file://" + str(file_path) + "/" + str(file_name) + " @aflac.public.azure_ips auto_compress = false overwrite=true ")
        
        #Cleanup the table before copying into:
        cur.execute(f"delete from {database_name}.{schema_name}.azureiplist_stg")
        cur.execute(f"copy into {database_name}.{schema_name}.{stage_name} from @azure_ips/"+file_name+ " file_format = (type = json)")

        cur.execute(f"describe network policy {network_policy}")

        #--------------------------------------------------------------------------------------------------------------------
        #   Base: 
        #      Fetch the IPs that are part of the current allow_list of your network policy
        #      
        #   1. Fetch only PowerBI IPs, these come in an array
        #   2. Uses higher order function "filter" to remove the IPV6 addresses from the array without requiring to flatten
        #   3. Compare this IP address list with the current network policy to add only the missing IPs
        #   4. Insert into a core table (current allow list, new azure ips, missing ips from allow list, alter statement)
        #--------------------------------------------------------------------------------------------------------------------

        cur.execute(f"""
                    insert into {database_name}.{schema_name}.azureiplist_core
                    with nw_pol as (
                            select strtok_to_array("value",',') current_allow_list
                              from table(result_scan(last_query_id()))
                      ),base as (
                            select array_distinct(filter(iplist, iplist -> iplist not like '%::%'))powerbi_ipv4
                              from (
                                      select value:"properties"."addressPrefixes" iplist
                                        from aflac.public.azureiplist_stg
                                            ,lateral flatten(input=> iplist:"values")
                                        where value:"name" = 'PowerBI'
                                 )
                      ) 
                 select  current_allow_list, 
                         powerbi_ipv4,  
                         array_except(powerbi_ipv4, current_allow_list) new_ips,
                         array_cat(current_allow_list, array_except(powerbi_ipv4, current_allow_list)) new_allow_list,
                         case 
                            when array_max(new_ips) is null then 'No New IPs this week' 
                            else  concat('alter network policy <policy name> set allowed_ip_list = (',
                                          replace(replace(replace(to_char(new_allow_list),'"',''''),'[',''),']',''),')'
                                     ) 
                         end as alter_str,
                         current_timestamp
                  from nw_pol, base;
        """)

        var = cur.fetchall()
        print(var)
    finally:
        cur.close()


def load_to_snowflake(config, file_path):
    logger = logging.getLogger()

    logger.info("uploader.py: load_to_snowflake()")        
    

    cur = setup_snowflake_conn (config)
    file_name = find_latest_file(file_path)  # We need to load the latest file in the file_path directory
    print("latest file:", file_name)
    validate_and_load(config, cur, file_path, file_name)



