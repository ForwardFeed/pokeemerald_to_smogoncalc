#!/bin/python3
import re
import jsonpickle
import yaml
import json
config = yaml.safe_load(open("./config.yml"))

def upcase_first_letter(s):
    return s[0].upper() + s[1:]

def formatRegular(text):
    text = text.strip().lower()
    return " ".join(list(map(upcase_first_letter, text.split("_")))).replace(',','')

def TargetParsing(target):
    if target == 'Both':
        return 'allAdjacentFoes'
    elif target == 'User':
        return 'self'
    elif target == 'Random':
        return False #should be randomNormal
    elif target == 'Foes And Ally"':
        return 'allAdjacent'
    elif target == 'Depends':
        return False #i dunno about this one
    elif target == 'All Battlers':
        return 'all'
    elif target == 'Opponents Field':
        return 'foeSide'
    elif target == 'Ally':
        return 'allies'
    '''
    global missedDict
    if target not in missedDict:
        global missedDict
        missedDict[target] = True
        print(target)'''
    return False

def FlagParsing(flag):
    if flag == 'FLAG_IRON_FIST_BOOST':
        return 'isPunch'
    elif flag == 'FLAG_KEEN_EDGE_BOOST':
        return 'isSlicing'
    elif flag == 'FLAG_AIR_BASED':
        return 'isAir'
    elif flag == 'FLAG_FIELD_BASED':
        return 'isField'
    elif flag == 'FLAG_ALWAYS_CRIT':
        return 'willCrit'
    elif flag == 'FLAG_STRIKER_BOOST':
        return 'isKick'
    elif flag == 'FLAG_HORN_BASED':
        return 'isHorn'
    elif flag == 'FLAG_STRONG_JAW_BOOST':
        return 'isBite'
    elif flag == 'FLAG_SOUND':
        return 'isSound'
    elif flag == 'FLAG_MEGA_LAUNCHER_BOOST':
        return 'isPulse'
    elif flag == 'FLAG_BALLISTIC':
        return 'isBullet'
    elif flag == 'FLAG_WEATHER_BASED':
        return 'isWeather'
    elif flag == 'FLAG_BONE_BASED':
        return 'isBone'
    elif flag == 'FLAG_SHEER_FORCE_BOOST':
        return 'secondaries'
    elif flag == 'FLAG_MAKES_CONTACT':
        return 'makesContact'
    elif flag == 'FLAG_TWO_STRIKES':
        return ('multihit', 2)
    elif flag == 'FLAG_STAT_STAGES_IGNORED':
        return 'ignoreDefensive'
    '''elif flag == 'FLAG_TARGET_ABILITY_IGNORED':
        return 'ignoreAbility'
        '''
    
    global missedDict
    if flag not in missedDict:
        missedDict[flag] = True
        print(flag)

def effectParsing(eff):
    if eff == 'EFFECT_RECOIL_33' or eff == 'EFFECT_RECOIL_33_STATUS':
        return ('recoil', [33, 100])
    elif eff == 'EFFECT_RECOIL_25' or eff == 'EFFECT_RECOIL_HP_25':
        return ('recoil', [1, 4])
    elif eff == 'EFFECT_RECOIL_IF_MISS':
        return ('recoil', [33, 100], 'hasCrashDamage')
    elif eff == 'EFFECT_RECOIL_50':
        return ('recoil', [1, 2])
    elif eff == 'EFFECT_ABSORB':
        return ('drain', [1,2])
    elif eff == 'EFFECT_TRIPLE_KICK':
        return('multihit', [1,3])
    return False

def AttrToAttr(attr, line):
    line = line.split(' = ')[1]
    line = line.replace(',','').replace('\n','')
    if attr == 'power':
        return ('bp', int(re.search('\d+', line).group()))
    elif attr == 'type':
        return ('type', formatRegular(re.search('(?<=TYPE_)\w+', line).group()))
    elif attr == 'split':
        return ('category',formatRegular(re.search('(?<=SPLIT_)\w+', line).group()))
    elif attr == 'accuracy':
        return ('acc',int(re.search('\d+', line).group()))
    elif attr == 'target':
        return ('target',TargetParsing(formatRegular(re.search('(?<=MOVE_TARGET_)\w+', line).group())))
    elif attr == 'priority':
        return ('priority', int(re.search('\d+', line).group()))
    elif attr == 'flags' or attr == 'flags2':
        listFlags = line.split(' | ')
        flagList = []
        for flag in listFlags:
            flag = FlagParsing(flag)
            if flag:
                flagList.append(flag)
        return ('flags', flagList)
    elif attr == 'secondaryEffectChance':
        return ('chance', int(re.search('\d+', line).group()))
    elif attr == 'argument':
        return ('arg', line)
    elif attr == 'effect':
        eff = effectParsing(line)
        if not eff:
            return False
        return eff
    else:
        '''
        global missedDict
        if attr not in missedDict:
            missedDict[attr] = True
            print('attr: ' + attr)'''
    return False
class Move:
    def __init__(self):
        self.bp = 0 #power
        self.type = "Normal"
        self.category = "" #split
        self.acc = 0 #accuracy
        self.target = ""
        self.priority = 0
        self.flags = []
        self.chance = 0 #secondaryEffectChance
        self.arg = "" #argument
    def addFlags(self, list):
        self.flags += list
file_moves = config['root'] + config['moves']

#allowed flags mean that if thoses are checked, it's like it's true.
allowedIFDEFFlags = {" REBALANCED_VERSION","B_USE_FROSTBITE == TRUE","B_UPDATED_MOVE_DATA >= GEN_4","B_UPDATED_MOVE_DATA >= GEN_6","B_UPDATED_MOVE_DATA >= GEN_5","B_UPDATED_MOVE_DATA >= GEN_7","B_UPDATED_MOVE_DATA != GEN_5","B_HIDDEN_POWER_DMG >= GEN_6","B_UPDATED_MOVE_DATA >= GEN_8","B_UPDATED_MOVE_DATA == GEN_6"}

moveDict = {}
name = ""
missedDict = {}
f_ifdef = True
with open(file_moves, 'r') as fp:
    lines = fp.readlines()
    for line in lines:
        #remove single line comments
        line = re.sub('//.*','',line)
        
        if re.search('\[MOVE_',line):
            name = re.search('(?<=\[MOVE_)\w+',line).group()
            name = formatRegular(name)
            moveDict[name] = Move()
            f_version = True
        if re.search('#if', line):
            case = re.search('((?<=if )|(?<=ifdef)).*', line)
            if case == None:
                print(line)
                continue
            case = case.group()
            if case in allowedIFDEFFlags:
                f_ifdef = True
            else:
                f_ifdef = False
        if re.search('#else', line):
            f_ifdef = not f_ifdef
        if re.search('#endif', line):
            f_ifdef = True
        if not f_ifdef:
            continue
        attribute = re.search('(?<=\.)\w+', line)
        if attribute == None:
            continue
        attribute = attribute.group()
        attribute = AttrToAttr(attribute, line)
        if attribute:
            if len(attribute) > 2:
                (a,b,c) = attribute
                if a == "flags":
                    moveDict[name].addFlags(b)
                else:
                    setattr(moveDict[name], a, b)
                setattr(moveDict[name], c, True)
            else:
                (a,b) = attribute
                if a == "flags":
                    moveDict[name].addFlags(b)
                else:
                    setattr(moveDict[name], a, b)
        
#trim data that can be implicitely found
finalMoveDict = {}
for moveName in moveDict.keys():
    move = moveDict[moveName]
    for flag in move.flags:
        if type(flag) is tuple or type(flag) is list:
            setattr(move, flag[0], flag[1])
        else:
            setattr(move, flag, True)
    del move.flags
    if move.target == False:
        del move.target
    if move.chance == 0:
        del move.chance    
    if move.arg == '':
        del move.arg
    elif (move.arg == 'STATUS1_PARALYSIS' or move.arg == 'MOVE_EFFECT_PARALYSIS'
    or move.arg == 'MOVE_EFFECT_FLINCH' or move.arg == 'TYPE_PSYCHIC'
    or move.arg == 'TRUE ' or move.arg == 'HOLD_EFFECT_MEMORY'
    or move.arg == 'STATUS1_BURN' or move.arg == 'TYPE_GRASS'
    or move.arg == 'TYPE_GHOST' or move.arg == 'MOVE_EFFECT_FEINT'
    or move.arg == 'MOVE_EFFECT_BURN' or move.arg == 'HOLD_EFFECT_DRIVE'
    or move.arg == 'STATUS1_SLEEP' or move.arg == 'HOLD_EFFECT_PLATE'
    or move.arg == 'STATUS1_FROSTBITE'):
        del move.arg
    elif move.arg == '75 ':
        move.drain = [3, 4]
        del move.arg
    elif move.arg == '100 ':
        move.drain = [1, 1]
        del move.arg
    elif move.arg == '50 ':
        move.drain = [1, 2]
        del move.arg
    elif move.arg == '25 ':
        move.drain = [1, 4]
        del move.arg
    
    finalMoveDict[moveName] = move

# manually pretify things the prettifier does't prettyfy
text = json.dumps(json.loads(jsonpickle.encode(finalMoveDict, unpicklable=False)),indent=2)
text = text.replace('"', '\'')
text = re.sub(r',\n[ ]{6}', ',', text)
text = re.sub(r'\n[ ]{6}', '', text)
text = re.sub(r'\n[ ]{4}\],', '],', text)
text = re.sub(r'\n[ ]{4}\},', '},', text)
text = re.sub(r'\n[ ]{4}\]', ']', text)

#print(jsonpickle.encode(ifDict, unpicklable=False))
output_file = open(config['moves_output'], 'w')
output_file.write(text)
output_file.close()
