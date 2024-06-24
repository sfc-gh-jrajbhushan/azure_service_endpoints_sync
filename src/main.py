# src/main.py
import yaml
import logging
from logger import setup_logger
from downloader import download_file
from uploader import load_to_snowflake
from urllib.parse import urlparse


def load_config(config_path='../config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def main():
    logger = setup_logger()
    config = load_config()
    logger.info("###################  Begin main.py:main() #######################")   

    try:
        # Download the Azure Service Tags from the public facing url (see config.yaml)
        download_file(config['download']['url'], config['download']['file_path'])

        # Upload the most recent file from the folder to Snowflake
        load_to_snowflake(config['database'], config['download']['file_path'])
    except Exception as e:
        logger.error(f"Process failed: {e}")

    logger.info("##################  End main.py:main() ##########################")   


if __name__ == '__main__':
    main()
