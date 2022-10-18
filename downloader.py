import requests
import json
import os
import pandas as pd

## Import the logging module
import logging
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("downloader.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

try:
    from config import config, var_dict, output_path
    logger.info("Successfully imported config dict from configuration file")
    logger.info("The AMR is {}".format(var_dict["drug_name"]))
    logger.info("The organism is {}".format(var_dict["organism"]))
    logger.info("The output directory is".format(output_path))

except Exception:
    logger.exception("Issue in loading the configuration file")


def read_file():
    """
    Read the csv file containing the genome IDs.
    If the csv file contains a column named "Genome ID",
    rename it "genome_id".

    return: Nothing to be returned
    """

    try:
     df = pd.read_csv(config["data_file"])
     logger.info("Successfully read the data file.")
     if "Genome ID" in df.columns:
         df.rename(columns={'Genome ID':'genome_id'},inplace=True)
         
     return df

    except Exception:
        logging.exception("Issue with reading file {}".format(config["data_file"]))


def compute_stats(dataframe):
    """
    For the pandas dataframe created from the csv file for a particular combination of 
    the organism and drug, this function will compute the number of NaNs in the column
    'genome_id'. It will return this value as a fraction of the total length of the 
    dataframe

    dataframe: Pandas dataframe. 
    return: Count of NaNs as a fraction of the lenght of the dataframe
    """
    try:
      
       logger.info("The number of rows in the dataframe is {}".format(len(dataframe)))
       nan_count = dataframe["genome_id"].isna().sum() 
       logger.info("The number of NaNs in the column genome_id is {}".format(nan_count))
       pct_count = (nan_count)/(len(dataframe))
       logger.info("The percentage of NaNs in the genome_id column is {}".format(pct_count*100))
       return pct_count
   
    except Exception:
       logger.exception("Error while computing NaN statistics")


def post_request(genome_id):
    """
    This function will make a POST request for the variable 'genome_id'. 
    The output of the POST request will be returned.
    
    genome_id: Number of float type, using which the POST request will be made
    return: Response object containing the response code and the data to be downloaded.
    """
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
    logger.info("The rql is {}".format(data))


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
     
      if len(response.text) == 0:
         logger.info("Empty output from POST request for genome id {}. Skipping this file".format(genome_id))
         return 

      with open(os.path.join(output_dir, filename), "w") as file_:
        file_.write(response.text)
      
        logger.info("FASTA file for genome ID {} successfully written to disk".format(genome_id))
        logger.info("The size of the file is {} bytes".format(len(response.text)))

            
    except Exception:
        logger.exception("Issue with writing FASTA file for genome ID {}".format(genome_id))
    


if __name__ == "__main__":
    
    logging.info("Beginning the execution of the program")

    df = read_file()
    pct_count = compute_stats(df)
    if pct_count == 1.0:
       logger.warning("All the files in the column are NaNs. Please check the file!! Stopping the download.")
       raise SystemExit
    
    df.dropna(subset=["genome_id"], inplace=True)
    ctr = 0
    exist_ctr = 0
    for genome_id in df["genome_id"]:

        logger.info("Genome ID is {}".format(genome_id))
        if os.path.exists(os.path.join(os.getcwd(),var_dict["fasta_dir"], str(genome_id)+'.fa')):
            exist_ctr += 1
            logger.info("FASTA file for genome with genome ID {} exists. Skipping the download for this".format(genome_id))
            continue
        response = post_request(genome_id=genome_id)
        write_post_req_to_fasta(response=response, genome_id=genome_id)
        

    logger.info("Program execution finished for organism:{} and AMR:{}".format(var_dict["organism"], var_dict["drug_name"]))
    logger.info("{} files already exist".format(exist_ctr))
