import os
import json
import re
import ast
import io

def convert(filePattern):
    files = [name for name in os.listdir() if re.match('.*_{0}.txt'.format(filePattern), name)]
    data = dict()
    for file in files:
        with open(file,'r', encoding = 'utf-8') as f:
            for line in f.readlines():
                data.update(ast.literal_eval(line[:-1]))
            f.close()
    with open('{0}Data.json'.format(filePattern),'w',encoding = 'utf-8') as file:
        json.dump(data, file)
        file.close()        

convert('detail')
convert('brief')

