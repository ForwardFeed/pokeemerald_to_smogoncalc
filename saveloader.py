#!/bin/python3
import re
import jsonpickle
import json
from copy import copy
import yaml

config = yaml.safe_load(open("./config.yml"))
file_abis = config['root'] + config['save_abis']
file_mons = config['root'] + config['save_mons']
file_moves = config['root'] + config['save_moves']
file_items = config['root'] + config['save_items']


def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def formatMacro(text):
    text = text.strip().lower()
    # i was hesistating to change " " to "-", but i think it's better with space
    return " ".join(list(map(upcase_first_letter, text.split("_"))))

def filterAbi(text):
    text = text.replace('ABILITY_', '')
    return formatMacro(text)
def filterMons(text):
    text = text.replace('SPECIES_', '')
    return formatMacro(text)
def filterMoves(text):
    text = text.replace('MOVE_', '')
    return formatMacro(text)
def filterItems(text):
    text = text.replace('ITEM_', '')
    return formatMacro(text)

def filterComments(line):
    return re.search('^((.*(?=\/\/))|(.*$))', line).group()

def isInDicOrInt(macro, dic):
    if macro in dic:
       return int(dic[macro])
    else:
       return int(macro)

def resolveComplexMacros(macro, dic):
    macro = re.findall('[^\s$]+', macro)
        
    # poor code quality but w/e
    macro[0] = isInDicOrInt(macro[0], dic)
    
    if len(macro) < 3:
        return macro[0]

    macro[2] = isInDicOrInt(macro[2], dic)
    
    return (macro[0] + macro[2])
    
def recurseAllMacros(file_path, dic = {}):
    prev_stuck = ""
    for r in range(0,10):
        dic = readAllMacros(file_path, dic)
        if not "MAYNEEDRECURSION" in dic:
            break
        if prev_stuck != dic["MAYNEEDRECURSION"]:
            prev_stuck = dic["MAYNEEDRECURSION"]
        else:
            break
        del dic["MAYNEEDRECURSION"]
        #print(str(r) + ' interation of ' + file_path)
    return dic
         

def readAllMacros(file_path, dic = {}):
    with open(file_path, 'r') as fp:
        lines = fp.readlines()
        for line in lines:
            line = filterComments(line)
            if re.search('#define\s', line):
                line = re.sub('#define\s+', '', line)
                macro = re.search('^\w+', line).group()
                line = re.sub("^" + macro + '(\s+)?', '', line)
                val = re.search('((?<=\()[^\)]+)|(\w+ \+ \w+$)', line) #in case of a complex one
                if val:
                    try:
                        val = resolveComplexMacros(val.group(), dic)
                    except ValueError:
                        if "MAYNEEDRECURSION" not in dic:
                            dic["MAYNEEDRECURSION"] = macro
                        continue

                else:
                    val = re.search('^\w+', line)
                    if not val:
                        continue
                    else:
                        try:
                            val = isInDicOrInt(val.group(), dic)
                        except ValueError:
                            if "MAYNEEDRECURSION" not in dic:
                                dic["MAYNEEDRECURSION"] = macro
                            continue
                dic[macro] = val
    return dic

def macroToArray(dic, pattern, nameFiltring):
    arr = [None] * len(dic.keys())
    for macro in dic.keys():
        if re.search(pattern, macro):
            val = int(dic[macro])
            arr[val] = nameFiltring(macro)
    return list(filter(lambda a: a != None, arr))

abis = macroToArray(readAllMacros(file_abis), "^ABILITY_", filterAbi)
abis = "var GEN3_ABILITIES = " + json.dumps(json.loads(jsonpickle.encode(abis, unpicklable=False)),indent=2)
mons = macroToArray(readAllMacros(file_mons), "^SPECIES_", filterMons)
mons = "var GEN3_MONS = " + json.dumps(json.loads(jsonpickle.encode(mons, unpicklable=False)),indent=2)
moves = macroToArray(readAllMacros(file_moves), "^MOVE_(?!LONG_)", filterMoves)
moves = "var GEN3_MOVES = " + json.dumps(json.loads(jsonpickle.encode(moves, unpicklable=False)),indent=2)
items = macroToArray(recurseAllMacros(file_items), "^ITEM_(?!USE_)(?!B_USE)", filterItems)
items = "var GEN3_ITEMS = " + json.dumps(json.loads(jsonpickle.encode(items, unpicklable=False)),indent=2)


text = abis.replace('\n', '') + '\n' + mons.replace('\n', '') + '\n' + moves.replace('\n', '') + '\n' + items.replace('\n', '') + '\n'

output_file = open(config['save_output'], 'w')
output_file.write(text)
output_file.close()


            
