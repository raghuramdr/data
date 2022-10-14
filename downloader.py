import requests
import json
import os
import pandas as pd

import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("downloader.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

try:
    from config import config
    logger.info("config imported successfully from config file")
except Exception:
    logger.exception("Issue in loading the configuration file")




def read_file():
    try:
     df = pd.read_csv(config["data_file"])
     logging.info("Successfully read the file {}".format(config["data_file"]))
     return df

    except Exception:
        logging.exception("Issue with reading file {}".format(config["data_file"]))


def post_request(genome_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-GB,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Origin': 'https://www.bv-brc.org',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://www.bv-brc.org/',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Sec-GPC': '1',
    }


    data = {
        'rql': 'in(genome_id%2C({}))%26sort(%2Bsequence_id)%26limit(2500000)'.format(genome_id),
    }
    logger.info("Data is {}".format(data))


    try:
        response=requests.post('https://patricbrc.org/api/genome_sequence/?&http_download=true&http_accept=application/dna+fasta', headers=headers, data=data)

        if response.status_code != 200:
            logger.warning("Genome ID {} has a problem. The response is {}".format(genome_id, response.status_code) )
        else:
            logger.info("Status code of genome with genome ID {} is {}".format(genome_id, response.status_code))
            return response

    except Exception:
        logger.exception("Error in the POST request")


def write_post_req_to_fasta(response, genome_id):

    """
    This function writes the sequence in the response obtained from a POST request to a FASTA file.
    The name of the FASTA file is the genome_id. 
    NOTE: The file is written to if it doesn't exist already. 
    There is no return value.

    response: Response object obtained from the successful POST request.
    genome_id: The name of the file and the genome ID for which the sequence is to be obtained.
    """
    filename = str(genome_id)+'.fa'
    try:
      with open(filename, "w") as file_:
        file_.write(response.text)
      file_size = os.stat(filename)
      
      if file_size.st_size>0:
        logger.info("FASTA file for genome ID {} successfully written to disk".format(genome_id))
        logger.info("The size of the file is {} bytes".format(file_size.st_size))

      else:
        logger.warning("FASTA file for genome ID {} is empty. Please check it! ".format(genome_id))


    except Exception:
        logger.exception("Issue with writing FASTA file for genome ID {}".format(genome_id))
    


if __name__ == "__main__":
    
    logging.info("Beginning the execution of the program")

    df = read_file()
    for genome_id in df["genome_id"]:

        logger.info("Genome ID is {}".format(genome_id))
        if os.path.exists(str(genome_id)+'.fa'):
            logger.info("FASTA file for genome with genome ID {} exists. Skipping the download for this".format(genome_id))
            continue
        response = post_request(genome_id=genome_id)
        write_post_req_to_fasta(response=response, genome_id=genome_id)
        

    logger.info("Program execution finished")


