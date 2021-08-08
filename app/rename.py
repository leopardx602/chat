
import os
import sys
path = sys.path[0] + '/static/img/egg'



for fname in os.listdir(path):
    print(fname)
    #print(len(fname))
    '''
    if len(fname) == 8:
        tk = fname[0:-5]
        id = '0' + fname[-5:-4]
        re = fname[-4:]
        newName = tk + id + re
        print(fname, newName)
        os.rename(os.path.join(path, fname), os.path.join(path, newName))
    '''
    '''
    if '_' in fname:
        pos = fname.find('_')
        newName = fname[0:pos]+'.png'
        print(newName)
        os.rename(os.path.join(path, fname), os.path.join(path, newName))
    '''


    '''if 'png' in fname:
        newName = fname[0:-2] + 'gif'
        os.rename(os.path.join(path, fname), os.path.join(path, newName))'''


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


