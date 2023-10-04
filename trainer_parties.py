#!/bin/python3
import re
import jsonpickle
from copy import copy
import yaml
config = yaml.safe_load(open("./config.yml"))

def cast_list(test_list, data_type):
    return list(map(data_type, test_list))

def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def formatRegular(text):
    text = text.strip().lower()
    return " ".join(list(map(upcase_first_letter, text.split("_")))).replace(',','')
    
def remMove(move):
    return formatRegular(move.replace('MOVE_',''))
  
def reformatTrainerName(name):
    name = name.replace('&', 'And')
    name = name.replace(' and ', ' And ')
    name = name.replace(' F ', ' ')
    name = name.replace(' M ', ' ')
    name = name.replace('Pokemon', 'Pkmn')
    name = name.replace('Pokéfan', 'Pokefan')
    name = name.replace('PKMN', 'Pkmn')
    name = name.replace('PokeManiac', 'Pokemaniac')
    name = name.replace('Sr and Jr', 'Sr. and Jr.')
    name = name.replace('Pkmn Trainer 3 ', '')
    return name
	
class TrainerName(object):
    def __init__(self):
        self.name = ""
        self.role = ""
        self.party = ""
        #self.inName = ""
    pass

file_trainers = config['root'] + config['trainers']

trainerNames = []
trainer = ""
with open(file_trainers, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        if re.match('    \[', line):
            trainer = TrainerName()
            trainer.name = re.search('(?<=    \[)[^\]]*', line).group().replace('TRAINER_','')
            trainer.name = formatRegular(trainer.name)
        if re.match('        .trainerClass', line):
            trainer.role = re.search('(?<=\= ).*', line).group().replace('TRAINER_CLASS_','')
            trainer.role = formatRegular(trainer.role)
        if re.match('        .partySize', line):
            trainer.party = re.search('(?<=\()[^\\)]*', line)
            if trainer.party == None:
                trainer.party = 0
            else:
                trainer.party = trainer.party.group().replace('sParty_','')
        '''if re.match('        .trainerName', line):
            trainer.inName = re.search('(?<=\= _\(\")[^\"]*', line).group()'''
        if re.match('    \},', line):
            trainerNames.append(trainer)
#print(json.dumps([ob.__dict__ for ob in trainers]))



class Trainer():
    def __init__(self):
        self.trn = ""
        self.mons = ""
class Pokemon():
    def __init__(self):
        self.level = 0
        self.species = ""
        self.item = ""
        self.ability = 0
        self.ivs = []
        self.evs = []
        self.nature = ""
        self.moves = []
file_parties = config['root'] + config['parties']
trainers = []
trainer = ""
pokes = []
poke = ""
pause = 0
with open(file_parties, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        line = re.sub('//.*','',line)
        if pause > 0:
            if re.search('\*/', line):
                pause -= 1
                continue
            else:
                continue;
        if re.search('[ ]*\/\*',line):
            pause += 1
            continue
        if re.match('^static', line):
            trainer = Trainer()
            trainer.trn = re.search('(?<=sParty_)[^\[]*', line).group()
        if re.search('^[ ]+{', line):
            poke = Pokemon()
        if re.search('.lvl', line):
            poke.level = int(re.search('(?<= = )\d*', line).group())
        if re.search('.species', line):
            poke.species = re.search('(?<= = )\w*', line).group().replace('SPECIES_','')
            poke.species = formatRegular(poke.species)
        if re.search('.heldItem', line):
            poke.item = re.search('(?<= = )\w*', line).group().replace('ITEM_','')
            poke.item = formatRegular(poke.item)
        if re.search('.ability', line):
            poke.ability = int(re.search('(?<= = )\w*', line).group())
        if re.search('.zeroSpeedIvs', line):
            poke.zeroSpe= True
        if re.search('.ivs', line):
            poke.ivs = re.findall('\d{1,3}', line)
            poke.ivs = cast_list(poke.ivs, int)
        if re.search('.evs', line):
            poke.evs = re.findall('\d{1,3}', line)
            poke.evs = cast_list(poke.evs, int)
        if re.search('.nature', line):
            poke.nature = re.search('(?<= = )\w*', line).group().replace('NATURE_','')
            poke.nature = formatRegular(poke.nature)
        if re.search('.moves', line):
            poke.moves = list(map(remMove,re.findall('( \w+)', line)))
        if re.match('[ ]+}', line):
            pokes.append(poke)
        if re.match('^};', line):
            trainer.mons = pokes
            trainers.append(trainer)
            pokes = []

def findParty(partyName):
    for party in trainers:
            if party.trn == partyName:
                return party.mons
    return None

class FinalTrainer():
    def __init__(self):
        self.trn = ""
        self.mons = ""
        self.rem = ["","","","",""]
        self.insane = ""
        self.alt = []
        self.opt_double = (False, False)
        self.double = False
        self.forc_double = False

newTrainers = {}
player = FinalTrainer()
player.trn = "Player"
player.mons = []
newTrainers['Player'] = player
for name in trainerNames:
    if not name.party:
        continue
    fullname = ""
    flagRem = False
    flagInsane = False
    
    if re.match(r'Grunt', name.name) == None:
        idn = re.search(r'\d+$',name.name)
        if idn == None:
            fullname = name.role + " " + name.name
        else:
            fullname = name.role + " " + re.sub(r' \d+$','',name.name)
            flagRem = re.search(r'\d+$',name.name)
            if (flagRem != None):
                flagRem = int(flagRem.group())
    else:
      fullname = name.role + " " + name.name
    if  re.search(r'Insane$',name.party):
        flagInsane = True
        
    if not newTrainers.get(fullname):
        newTrainers[fullname] = FinalTrainer()
        newTrainers[fullname].trn = reformatTrainerName(fullname)
    if flagInsane == True:
        newTrainers[fullname].insane = findParty(name.party)
        newTrainers[fullname].mons = findParty(re.sub(r'Insane','',name.party))
    elif flagRem == False:
        newTrainers[fullname].mons = findParty(name.party)
    elif flagRem == None:
        newTrainers[fullname].mons = findParty(name.party)
    else:
        if flagRem == 1:
            newTrainers[fullname].mons = findParty(name.party)
        else:
            newTrainers[fullname].rem[flagRem - 2] = findParty(name.party)


def trimTrainer(trainer):
    if trainer == "":
        return False
    if trainer.insane == "":
        del trainer.insane
    if trainer.mons == "":
        if trainer.rem[0] == "":
            return False
        else:
            trainer.mons = trainer.rem[0]
            del trainer.rem[0]
    trainer.rem = list(filter(lambda x: (x != "") , trainer.rem))
    if len(trainer.rem) == 0:
        del trainer.rem
    if len(trainer.alt) == 0:
        del trainer.alt
    if trainer.opt_double == (False, False):
        del trainer.opt_double
    if trainer.double == False:
        del trainer.double
    if trainer.forc_double == False:
        del trainer.forc_double
    return trainer

def filterTrainerName(trnName):
    trnName = trnName.strip()
    dataT = re.sub('(({)|(}))', '', trnName)
    dataT = re.sub('\[.*\]', '', dataT)
    nameT = re.sub('{.*}', '', trnName)
    nameT = re.sub('((\[)|(\]))', '', nameT)
    return (dataT,nameT)

def findTrainer(trnName, allow_duplicate):
    if trnName in newTrainers:
        trainer = copy(newTrainers[trnName])
        if not allow_duplicate:
            del newTrainers[trnName]
        return  trainer
    else:
        #because of the reformatTrainerName
        for key in newTrainers.keys():
            trainer = newTrainers[key]
            if trainer.trn == trnName:
                trainer = copy(trainer)
                if not allow_duplicate:
                    del newTrainers[key]
                return trainer
        return False

# reorder trainers
file_order = config['order']
missed = []
maps = []
count = 0
trainer = ""
f_prevOpt = False
trainer_dex = []
with open(file_order, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        f_optional = False     #?
        f_double = False       #=
        f_opt_double = False   #*
        f_forc_double = False  #!
        allow_duplicate = False#+
        if re.search('^%.*%$',line):
            route = re.search('(?<=%).*(?=%)', line).group()
            maps.append((route, count))
            continue
        #comments
        if re.match('((\#)|(---))', line):
            continue
        if re.search('\?', line):
            f_optional = True
            line = line.replace('?','')
        if re.search('=', line):
            f_double = True
            line = line.replace('=','')
        if re.search('\*', line):
            f_opt_double = True
            line = line.replace('*','')
        if re.search('!', line):
            f_forc_double = True
            line = line.replace('!','')
        if re.search('\+', line):
            allow_duplicate = True
            line = line.replace('+','')
        line = line.split(',')
        if len(line) == 0:
            f_prevOpt = False
            continue
        if len(line) == 1:
            line = ''.join(line)
            dataT, nameT = filterTrainerName(line)
            trainer = findTrainer(dataT,allow_duplicate)
            if not trainer:
                missed.append(nameT)
                continue
            if f_optional:
                trainer.trn = nameT + ' (Opt.)'
                trainer.opt = True
            else:
                trainer.trn = nameT
            trainer.double = f_double
            trainer.opt_double = (f_prevOpt, f_opt_double)
            if f_opt_double:
                f_prevOpt = True
            else:
                f_prevOpt = False
            trainer.forc_double = f_forc_double

            trainer = trimTrainer(trainer)
            if not trainer:
                continue
            trainer_dex.append(trainer)
            count +=1
        else:
            dataT, nameT = filterTrainerName(line[0])
            del line[0]
            trainer = findTrainer(dataT,allow_duplicate)
            if not trainer:
                missed.append(nameT)
                continue
            trainer.trn = nameT
            for alt in line:
                dataT, nameT = filterTrainerName(alt)
                trainerAlt = findTrainer(dataT,allow_duplicate)
                if not trainerAlt:
                    missed.append(dataT)
                    continue
                trainerAlt.trn = nameT
                trainer.alt.append(trimTrainer(trainerAlt))
            trainer = trimTrainer(trainer)
            if not trainer:
                continue
            trainer_dex.append(trainer)
            count +=1
            
            
            
#trim data
for index in newTrainers.keys():
    trainer = newTrainers[index]
    trainer = trimTrainer(trainer)
    if not trainer:
        continue 
        
    trainer_dex.append(trainer)

#make forced double
for i, trainer in enumerate(trainer_dex):
    if hasattr(trainer, 'forc_double'):
        next_trn = trainer_dex[i + 1]
        trainer.trn += ' & ' + next_trn.trn
        trainer.mons = trainer.mons + next_trn.mons
        if hasattr(trainer, 'alt'):
            print('TODO FORCED ALT' + trainer.trn)
        if hasattr(trainer, 'rem'):
            print('TODO FORCED REM' + trainer.trn)
    trainer_dex[i] = trainer


output_file = open(config['trainers_output'], 'w')
output_file.write("var TRAINER_DEX =" + jsonpickle.encode(trainer_dex, unpicklable=False))
output_file.close()
output_file = open(config['trainers_map_output'], 'w')
output_file.write(jsonpickle.encode(maps, unpicklable=False))
output_file.close()

print('missed :' + jsonpickle.encode(missed, unpicklable=False))
print('total included', len(trainer_dex))
print('total not ordered', len(newTrainers.keys()))



