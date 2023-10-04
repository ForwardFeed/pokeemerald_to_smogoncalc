#!/bin/python3

import argparse
import yaml
#### START OF ARGUMENT PARSING ####

parser = argparse.ArgumentParser(
                    prog='pokeemerald_to_calc',
                    description='Import data from pokeEmerald to UNC type calc')

parser.add_argument('--update',
                    help='update the repository (TODO)')

args = parser.parse_args()


#### END OF ARGUMENT PARSING ####

def updateRepository():
    #TODO
    return
    

config = yaml.safe_load(open("./config.yml"))
print(config['root'] + config['trainers'])

