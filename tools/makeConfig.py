# Author: Alex
# Date: 3/6/2024
# This is a helper program for the file mover. It creates the config files that the auto scripts use

# If it breaks contact Alex

import configparser
import os

def __make_config(config_data: tuple) -> None:

    config = configparser.ConfigParser()

    config['Login'] = {'user': config_data[0],
                       'password': config_data[1],}

    config['Email'] = {'sender': config_data[2],
                       'reveiver': config_data[3],
                       'password': config_data[4]}

    with open('config.ini', 'w') as configfile:
        config.write(configfile)

def __get_inputs():
    print("--- Machine Login ---")
    user = input("What is the username? - ")
    machine_pass = input("What is the password? - ")
    print("--- Email Login ---")
    sender = input("Sender email - ")
    email_pass = input("Sender password - ")
    receiver = input("Receiver email - ")

    return user, machine_pass, sender,receiver ,email_pass

if __name__ == "__main__":
    os.chdir("..")
    __make_config(__get_inputs())
    
