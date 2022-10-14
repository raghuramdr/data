### This README file contains a Python script to perform a POST request to download genomes from the BVBRC [website](https://www.bv-brc.org/)
### BV-BRC is a repository that stores genomes of micro-organisms such as bacteria, viruses, etc. 


## How to use this script to download the data?
### The codebase contains two scripts, *config.py* and *downloader.py*. 
### You will need to make some changes in the  *config.py* before starting the download. To do this, open the file *config.py* and change the name of the value corresponding to the key **organism** to your desired organism. Please ensure that there is a directory by this name, otherwise you will get an error. Likewise, also do this for the key **drug_name**, and ensure that a directory with exactly the same name exists.

##  Install virtualenv
`pip install virtualenv`
### on your terminal.

## Create a virtualenv
`virtualenv <name_of_the_virtual_environment>`
### The angular brackets is used to denote that this is a user defined name. Don't enter the angular brackets when running the command.

## Activate the virtual environment
`source </path/to/virtual/environment/>/bin/activate`

## Install the requirements file
`pip install -r requirements.txt`

## NOTE: If you already have done any or all of the steps above, skip it.

### To start the download, run the file *downloader.py* in your Terminal after making the necessary changes to *config.py* as explained above.



