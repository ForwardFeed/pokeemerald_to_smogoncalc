#!/bin/python3
import re
import jsonpickle
import json
from copy import copy
import yaml
config = yaml.safe_load(open("./config.yml"))

def abiFilter(abi):
    if abi != 'None':
        return True
    return False
    
def abiFormat(abi):
    return abis_corrections[abi].replace("'", "\\'")

def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def formatSpecies(text):
    text = text.strip().lower()
    # i was hesistating to change " " to "-", but i think it's better with space
    return " ".join(list(map(upcase_first_letter, text.split("_"))))
    
def formatRegular(text):
    text = text.strip().lower()
    return " ".join(list(map(upcase_first_letter, text.split("_"))))

def abilityNaming():
    dic = {}
    file_abis = config['root'] + config['abilities']
    whenRead = False
    with open(file_abis, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            if not whenRead and re.search('gAbilityNames', line):
                whenRead = True
                continue
            if re.search('gAbilityDescriptionPointers', line):
                break
            if re.search('\[ABILITY_', line):
                macro = re.search('ABILITY_[^\]]+', line).group()
                val = re.search('(?<=\").*(?=\")', line).group()
                dic[macro] = val
    return dic
abis_corrections = abilityNaming()

file_species = config['root'] + config['species']
file_entries = config['root'] + config['entries']
file_formes = config['root'] + config['formes']
file_stats = config['root'] + config['base_stats']
file_evo = config['root'] + config['evo']

class BaseStats:
    def __init__(self):
        self.hp = 0
        self.at = 0
        self.df = 0
        self.sa = 0
        self.sd = 0
        self.sp = 0
        
class Pokemon:
    def __init__(self):
        self.id = ""
        self.bs = BaseStats()
        self.abilities = []
        self.innates = []
        self.otherFormes = []
        self.nfe = False
        self.baseSpecies = ""
        self.heads = 0
        self.weightkg = 0
        self.types = []
        
pokedex = {}
idCount = 0
poke = ""
# import id, name
with open(file_species, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if re.search('#define SPECIES_', line):
            species = formatSpecies(re.search('(?<=SPECIES_)\w+', line).group())
            pokedex[species] = Pokemon()
            pokedex[species].id = idCount
            idCount += 1
            
species = ""
# import weightkg
with open(file_entries, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if re.search('[ ]*\[\w', line):
            species = re.search('(?<=\[)[^\]]+', line).group().replace('NATIONAL_DEX_','')
            species = formatSpecies(species)
        if re.search('[ ]*\.weight', line):
            pokedex[species].weightkg = int(re.search('\d+', line).group())
            
#import other formes
species = ""
start = 0
with open(file_formes, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if start == 0:
            if re.search('u16 s', line):
                start = - 1
            continue
        if start == -1:
            if re.search(' SPECIES_', line):
                species = re.search('SPECIES_\w+', line).group().replace('SPECIES_','')
                species = formatSpecies(species)
                start = 1
            continue
        if re.search(' SPECIES_', line):
            forme = re.search('SPECIES_\w+', line).group().replace('SPECIES_','')
            forme = formatSpecies(forme)
            pokedex[species].otherFormes.append(forme)
            if not forme in pokedex:
                # copy the same traits, with exceptions
                pokedex[forme] = copy(pokedex[species])
                pokedex[forme].types = []
                pokedex[forme].otherFormes = [species]
            pokedex[forme].otherFormes.append(species)
            continue
        if re.search(' FORM_SPECIES_END', line):
            start = 0

            
#import base stats, type, (?growth rate maybe?later)
species = ""
pause = 0
with open(file_stats, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if pause > 0:
            if re.search('\*/', line):
                pause -= 1
                continue
            else:
                continue
        if re.search('[ ]*\/\*',line):
            pause += 1
            continue
        if re.search('[ ]*\[\w', line):
            species = re.search('(?<=\[)[^\]]+', line).group().replace('SPECIES_','')
            species = formatSpecies(species)
            
        if re.search('[ \t]+\.baseHP', line):
            pokedex[species].bs.hp = int(re.search('\d+', line).group())
        if re.search('[ \t]+\.baseAttack', line):
            pokedex[species].bs.at = int(re.search('\d+', line).group())
        if re.search('[ \t]+\.baseDefense', line):
            pokedex[species].bs.df = int(re.search('\d+', line).group())
        if re.search('[ \t]+\.baseSpeed', line):
            pokedex[species].bs.sp = int(re.search('\d+', line).group())
        if re.search('[ \t]+\.baseSpAttack', line):
            pokedex[species].bs.sa = int(re.search('\d+', line).group())
        if re.search('[ \t]+\.baseSpDefense', line):
            pokedex[species].bs.sd = int(re.search('\d+', line).group())
        
        if re.search('[ \t]+\.type', line):
            types = formatRegular(re.search('(?<=TYPE_)\w+', line).group())
            pokedex[species].types.append(types)
        if re.search('[ \t]+\.genderRatio', line):
            genderR = 255
            if re.search('PERCENT_FEMALE', line):
                genderR = int(re.search('\d+', line).group())
                genderR = int(min(254, ((genderR * 255) / 100)))
            if re.search('MON_MALE', line):
                genderR = 0
            if re.search('MON_FEMALE', line):
                genderR = 254 
            pokedex[species].genderR = genderR
        if re.search('[ ]+\.abilities', line):
            pokedex[species].abilities = list(map(abiFormat,re.findall('ABILITY\w+', line)))
        if re.search('[ ]+\.innates', line):
            pokedex[species].innates = list(map(abiFormat,re.findall('ABILITY\w+', line)))

species = ""
with open(file_evo, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if re.search('\[SP',line):
            species = formatSpecies(re.search('(?<=\[SPECIES_)\w+',line).group())
            if not re.search('MEGA',line):
                pokedex[species].nfe = True

#trim data that can be implicitely found
finalDex = {}
for species in pokedex.keys():
    poke = pokedex[species]
    if poke.nfe == False:
        del poke.nfe
    if not poke.baseSpecies:
        del poke.baseSpecies
    if poke.heads == 0:
        del poke.heads
    if len(poke.otherFormes) < 1:
        del poke.otherFormes
    if len(poke.types) > 1 and poke.types[0] == poke.types[1]:
        del poke.types[1]
    if len(poke.abilities) < 1:
        continue
    if len(poke.innates) < 1:
        continue
    poke.innates = list(filter(abiFilter, poke.innates))
    if len(poke.innates) < 1:
        poke.innates = ['']
    if len(poke.abilities) < 1:
        continue
        
    finalDex[species] = poke

text = json.dumps(json.loads(jsonpickle.encode(finalDex, unpicklable=False)),indent=2)
# manually pretify things the prettifier does't prettyfy
text = text.replace('"hp"', 'hp')
text = text.replace('"at"', 'at')
text = text.replace('"df"', 'df')
text = text.replace('"sp"', 'sp')
text = text.replace('"sd"', 'sd')
text = text.replace('"sa"', 'sa')
text = text.replace('"nfe"', 'nfe')
text = text.replace('"baseSpecies"', 'baseSpecies')
text = text.replace('"heads"', 'heads')
text = text.replace('"genderR"', 'genderR')
text = text.replace('"weightkg"', 'weightkg')
text = text.replace('"types"', 'types')
text = text.replace('"bs"', 'bs')
text = text.replace('"otherFormes"', 'otherFormes')
text = text.replace('"abilities"', 'abilities')
text = text.replace('"innates"', 'innates')
text = text.replace('"id"', 'id')
text = text.replace('"', '\'')
text = text.replace('\\\\', '\\')
text = re.sub(r',\n[ ]{6}', ',', text)
text = re.sub(r'\n[ ]{6}', '', text)
text = re.sub(r'\n[ ]{4}\],', '],', text)
text = re.sub(r'\n[ ]{4}\},', '},', text)

output_file = open(config['pokedex_output'], 'w')
output_file.write(text)
output_file.close()




