#!/bin/python3
import re
import jsonpickle
import yaml
config = yaml.safe_load(open("./config.yml"))

def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def formatRegular(text):
    text = text.strip().lower()
    return " ".join(list(map(upcase_first_letter, text.split("_"))))

class AbilityDesc:
    def __init__(self):
        self.desc = ""
class AbilityID:
    def __init__(self):
        self.IGName = ""
class Ability:
    def __init__(self):
        self.IGName = ""
abilist = []
FinalAbiDescDic = {}
abiDescObj = {}
abiObj = {}
file_abi = config['root'] + config['abilities']
with open(file_abi, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if re.search('u8 s', line):
            descID = re.search('(?<=u8 s)\w+(?=Description)', line).group()
            abiDescObj[descID] = AbilityDesc()
            desc = re.search('(?<=\(\")[^\"]*', line).group()
            desc = desc.replace('\\n',' ')
            abiDescObj[descID].desc = desc
        elif re.search('\[ABILITY_', line):
            abiID = re.search('ABILITY_[^]]+', line).group()
            if abiID in abiObj:
                descID = re.search('(?<= s)\w+(?=Description)', line).group()
                FinalAbiDescDic[abiObj[abiID].IGName] = abiDescObj[descID].desc
            else:
                abiObj[abiID] = AbilityID()
                IGName = re.search('(?<=\(\")[^\"]*', line)
                if IGName == None:
                    print(line)
                else:
                    IGName = IGName.group()
                    abiObj[abiID].IGName = IGName
                    abilist.append(IGName)


output_file = open(config['abilities_output'], 'w')
output_file.write(jsonpickle.encode(abilist, unpicklable=False))
output_file.close()
output_file = open(config['abilities_description_output'], 'w')
output_file.write('var ABI_DESC = ')
output_file.write(jsonpickle.encode(FinalAbiDescDic, unpicklable=False))
output_file.close()
# moves.py
