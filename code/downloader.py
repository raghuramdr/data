import os
import requests

import argparse as ap
import pandas as pd

## Import the logging module
import logging

from custom_logger import CustomFormatter

#TODO: Needs to be moved into custom_logger.py and the previous LOC will be deleted
def set_logger(config):
    """
    This function customizes the log handler

    config: Object of type argparse.
    return: logger object
    """

    logger=logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    if not os.path.exists(os.path.join(os.getcwd(), config.pathogen, "logs")):
        os.mkdir(os.path.join(os.getcwd(), config.pathogen, "logs"))
        
    file_handler = logging.FileHandler(os.path.join(os.getcwd(), config.pathogen, "logs", "download_{}_{}.log".format(config.pathogen, config.anti_microbial)))
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch) 

    return logger


def read_file(filepath):
    """
    Read the csv file containing the genome IDs.
    If the csv file contains a column named "Genome ID",
    rename it "genome_id".
    
    filepath: Full path to the CSV file containing the genome IDs
    return: Pandas dataframe containing genome IDs 
    """

    try:
     assert os.path.exists(filepath), "File does not exist."
     df = pd.read_csv(filepath, on_bad_lines='skip', engine="python")
     if df is None:
        logger.critical("The dataframe is of None type. Cannot proceed ahead! Please check! EXITING!")
        raise SystemExit
     logger.info("Successfully read the data file.")
     if "Genome ID" in df.columns:
         df.rename(columns={'Genome ID':'genome_id'},inplace=True)
         
     return df
 
    except AssertionError:
        logger.error("The file does not exist at path {}".format(filepath))
    
    except Exception:
       logger.exception("Issue with reading file at location {}".format(filepath))



def check_amr_name(anti_microbial_name_user, anti_microbial_name_file):
    
    """
    This function compares the user supplied name of the anti microbial with 
    the name of the anti microbial in the CSV file. It returns a boolean flag depending on the 
    result of the comparison.
    
    anti_microbial_name_user: The name of the anti microbial supplied by the user
    anti_microbial_name_file: The name of the anti microbial read from the file
    return: True (bool) if same, else False
    """
    
    if anti_microbial_name_file is None:
        logger.warning("The file doesn't containg the name of the drug. Please make sure you have entered the correct name!!")
        return True

    anti_microbial_name_user, anti_microbial_name_file = anti_microbial_name_user.lower(), anti_microbial_name_file.lower()
    logger.info("The name of the anti microbial entered by you is {}".format(anti_microbial_name_user))
    logger.info("The name of the anti microbial as per the file is {}".format(anti_microbial_name_file))
    if anti_microbial_name_user == anti_microbial_name_file:
        logger.info("Names match!")
        return True
    else:
        logger.warning("Names do not match!")
        return False
   

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
    #TODO: Pass the headers and URL as an argument which is imported from config.py
    """


    data = {
        'rql': 'in(genome_id%2C({}))%26sort(%2Bsequence_id)%26limit(2500000)'.format(genome_id),
    }
    logger.info("The rql is {}".format(data))


    try:
        response=requests.post(config["URL"], headers=config["headers"], data=data)

        if response.status_code != 200:
            logger.warning("Genome ID {} has a problem. The response is {}".format(genome_id, response.status_code) )
        else:
            logger.info("Status code of genome with genome ID {} is {}".format(genome_id, response.status_code))
            return response

    except Exception:
        logger.exception("Error in the POST request")


def write_post_req_to_fasta(response, genome_id, write_path):

    """
    This function writes the sequence in the response obtained from a POST request to a FASTA file.
    The name of the FASTA file is the genome_id. 
    NOTE: The file is written to if it doesn't exist already. 
    There is no return value.

    response: Response object obtained from the successful POST request.
    genome_id: The name of the file and the genome ID for which the sequence is to be obtained.
    write_path: The full path of the directory to where the files will be written to.
    """
    filename = str(genome_id)+'.fa'
    try:
     
      if len(response.text) == 0:
         logger.info("Empty output from POST request for genome id {}. Skipping this file".format(genome_id))
         return 

      with open(os.path.join(write_path, filename), "w") as file_:
        file_.write(response.text)
      
        logger.info("FASTA file for genome ID {} successfully written to disk".format(genome_id))
        logger.info("The size of the file is {} bytes".format(len(response.text)))

            
    except Exception:
        logger.exception("Issue with writing FASTA file for genome ID {}".format(genome_id))
    

def set_parameters():

    """
    Function to accept user defined parameters.

    return: argparse object named config
    """

    try:
      parser = ap.ArgumentParser(description="Read CSV files and download FASTA files corresponding to the genome IDs in the CSV files.")
      parser.add_argument("--pathogen", type=str, required=True, help="The name of the pathogen for which the data has to be downloaded. There should be a corresponding directory with the exact same name!")
      parser.add_argument("--anti_microbial", type=str, required=True, help="The name of the anti microbial. There has to be a folder with the exact same name.")
      parser.add_argument("--filename", type=str, required=True, help="The name of the CSV file.") 
      args =  parser.parse_args()
      return args
    
    except Exception:
        print("Issue in setting parameters")


def set_paths(config):
    
    """
    Function to set paths for the output directory and the input files.

    config: Argparse object
    return: Dictionary containing the output directory and the input files as values.
    """

    try:
     path_dict = {}
     path_dict["filepath"] = os.path.join(os.getcwd(), config.pathogen, config.anti_microbial, config.filename)
     path_dict["write_path"] = os.path.join(os.getcwd(), config.pathogen, "fasta_files")
     
     if not os.path.exists(path_dict["write_path"]):
        os.mkdir(path_dict["write_path"])
    
     logger.info("File path is {}".format(path_dict["filepath"]))
     logger.info("Write destination is {}".format(path_dict["write_path"])) 
     return path_dict
   
    except Exception:
      logger.exception("Issue while setting paths.")


if __name__ == "__main__":
    
    config = set_parameters()
    logger = set_logger(config)
    path_dict = set_paths(config)

    logger.info("The name of the pathogen is {}".format(config.pathogen))
    logger.info("The name of the anti microbial is {}".format(config.anti_microbial))
    logger.info("The filename is {}".format(config.filename)) 
    
 
    df = read_file(path_dict["filepath"]) 

    if df.Antibiotic.nunique() != 1:
        logger.warning("Multiple drugs in this file. Please check the file again.")
        raise SystemExit

    else:
      amr_file_name = df["Antibiotic"].unique()[0]
      check_flag = check_amr_name(anti_microbial_name_user = config.anti_microbial, 
            anti_microbial_name_file = amr_file_name)
    
    if not check_flag:
       logger.warning("Exiting the program due to mismatch!")
       raise SystemExit

    pct_count = compute_stats(df)
   
    if pct_count == 1.0:
       logger.warning("All the files in the column are NaNs. Please check the file!! Stopping the download.")
       raise SystemExit
    
    df.dropna(subset=["genome_id"], inplace=True)
    ctr = 0
    exist_ctr = 0
    for genome_id in df["genome_id"]:

        logger.info("Genome ID is {}".format(genome_id))
        if os.path.exists(os.path.join(path_dict["write_path"], str(genome_id)+'.fa')):
            exist_ctr += 1
            logger.info("FASTA file for genome with genome ID {} exists. Skipping the download for this".format(genome_id))
            continue
        response = post_request(genome_id=genome_id)
        write_post_req_to_fasta(response=response, genome_id=genome_id, write_path=path_dict["write_path"])
    

    logger.info("Program execution finished!")
    logger.info("{} files already exist".format(exist_ctr))

