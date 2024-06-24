-- Pick your database & Schema
create stage azure_ips;

create or replace table azureiplist_stg (
    iplist variant
);

create or replace table azureiplist_core (
    current_allow_list variant,
    azure_powerbi_list variant,
    new_ip_addresses variant,
    new_allow_list variant,
    alter_nw_policy varchar,
    load_ts timestamp default current_timestamp
);

