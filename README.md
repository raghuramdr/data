### This README file contains a Python script to perform a POST request to download genomes from the BVBRC [website](https://www.bv-brc.org/)
### BV-BRC is a repository that stores genomes of micro-organisms such as bacteria, viruses, etc. 


## Before starting the download, follow the steps below

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

### To start the download, run the file *downloader.py* in the following manner.

`python downloader.py --p <name_of_the_pathogen> --a <name_of_the_anti_microbial> --f <filename.csv>` 

### The code looks for a folder with the following directory structure, <cwd/name_of_the_pathogen/name_of_the_anti_microbial/filename.csv>
### So ensure that the folder names and directory structure matches as per this convention

