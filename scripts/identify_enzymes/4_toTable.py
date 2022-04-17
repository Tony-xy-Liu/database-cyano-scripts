import os
import numpy as np

################################################################
# no adaptation required
################################################################

ROOT = os.environ['ROOT']
LAYERS = 'reactions, enzymes, proteins'.split(', ')

csvs_by_layer:dict[str, list] = {}
for name in LAYERS:
    csvs_by_layer[name] = []

print('calculating')

alls = []
for a in range(4):
    alls.append(dict())

files = os.listdir(f'{ROOT}/trace/')
fileNum = 0
for tpath in files:
    fileNum += 1
    summ, r, e, p = np.load(f'{ROOT}/trace/{tpath}', allow_pickle=True)
    layers = r, e, p
    summ = summ.split(".")[0]

    for all, layer, lname in zip(alls, layers, LAYERS):
        csv = csvs_by_layer[lname]

        one_hot = ["0"]*len(all)
        for attr in layer:
            if attr in all:
                one_hot[all[attr]] = "1"
            else:
                all[attr] = len(all)
                one_hot.append("1")
        
        csv.append((summ, one_hot))

print('\ncompiling')

SEP = '\t'
os.system(f"mkdir -p {ROOT}/tables/")
for columns, cbl in zip(alls, csvs_by_layer.items()):
    lname, csv = cbl
    with open(f'{ROOT}/tables/layer_{lname}.tsv', 'w') as tsv:
        tsv.seek(0)
        tsv.write(f"{SEP.join(['FileID']+list(columns))}\n") # header
        for summ, one_hot in csv:
            tsv.write(f"{SEP.join([summ]+one_hot+['0']*(len(columns)-len(one_hot)))}\n")
        tsv.truncate()