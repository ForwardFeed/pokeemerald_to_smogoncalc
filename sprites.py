#!/bin/python3
from PIL import Image
from os import listdir, path, makedirs
import yaml

config = yaml.safe_load(open("./config.yml"))
folder = config['root'] + config['sprites']


if not path.isdir(config['sprites_output']):
    makedirs(config['sprites_output'])

count = 0

def upperA(text):
    return text.title()
    
def fixName(name):
    name = name.replace('/', '_')
    name = name.split('_')
    name = list(map(upperA, name))
    if len(name) == 0:
        return name
    elif len(name) == 1:
        return name[0]
    else:
        last = name[len(name) - 1]
        if last == 'X' or last == 'Y':
            temp = name[len(name) - 2]
            name[len(name) - 2] = name[0]
            name[0] = temp
            return ' '.join(name)
        first = name [0]
        if first == 'Mega' or first == 'Alolan' or first == 'Galarian' or first == 'Primal':
            temp = name[len(name) - 1]
            name[len(name) - 1] = name[0]
            name[0] = temp
            return ' '.join(name)
        return ' '.join(name)
        
        
    
def generate(folder, name):
    global count, missed
    fullpath = folder + name + '/icon.png'
    if not path.isfile(fullpath):
        return
    img = Image.open(fullpath)
    # crop only to take the top icon
    img = img.crop((0, 0, 32, 32))
    # add a transparency layer
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    # the first pixel is considered the transparency color
    trns = datas[0]
    for item in datas:
        if item == trns:
            # replace by a transparent pixel
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    count += 1
    savename = fixName(name)
    img.save(config['sprites_output'] + savename + '.png', "PNG")
    #formes of a pokemon are in the same folder
    form_dirs = listdir(folder + name)
    if len(form_dirs) > 0:
        for form in form_dirs:
            generate(folder, name + '/' + form)
    
dirs = listdir(folder)
for name in dirs:
    generate(folder, name)
print("There was " + str(len(dirs)) + " items in the folder" )
print("generated in total: " + str(count) + " sprites")

