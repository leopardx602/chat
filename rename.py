
import os
import sys
path = sys.path[0] + '/static/img/classic'



for fname in os.listdir(path):
    #print(fname)
    '''
    if '_' in fname:
        pos = fname.find('_')
        newName = fname[0:pos]+'.png'
        print(newName)
        os.rename(os.path.join(path, fname), os.path.join(path, newName))'''


    if 'pn' in fname:
        newName = fname[0:-2] + 'gif'
        os.rename(os.path.join(path, fname), os.path.join(path, newName))


'''
for fname in os.listdir(path):
    #print(fname)

    number = filter(str.isdigit, fname)
    number = int(''.join(list(number)))+1
    if 'gif' in fname:
        newName = 'tiger{}.gif'.format(number)
    elif 'png' in fname:
        newName = 'tiger{}.png'.format(number)
    os.rename(os.path.join(path, fname), os.path.join(path, newName))'''


