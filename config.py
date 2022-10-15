import os

import logging

logger=logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("config.log")
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)


logger.info("Opening the configuration file")
cwd = os.getcwd()

var_dict = {"organism":"klebsiella_pneumoniae", "drug_name":"amikacin", "fasta_dir":"fasta_files"}
## The data path is always PWD/organism/drug_name
## If you need to change it change only the organism name and the name of the drug 
## in argument of the code below
try:
	data_path = os.path.join(cwd, var_dict["organism"], var_dict["drug_name"])
except Exception:
	logger.exception("Issue with data path")

try:
    output_path = os.path.join(cwd, var_dict["fasta_dir"])
except Exception:
    logger.exception("Issue with the fasta_dir variable in var_dict.")

##file_name is the name of the file to fetch the genome IDs from
file_name = "BVBRC_genome_amr.csv"

try:
	config = {"data_file": os.path.join(data_path, file_name)}
except Exception:
	logger.exception("Issue with file {}".format(file_name))


