import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

#####################################################################################################
# adapt to parse your output table

def parseLine(line, found):
    # example line: "3	UniRef100_A0LPR8 Uncharacterized protein # K09949    7.30e-64	229"

    toks1 = line.split('\t')
    # [1, "UniRef100_A0LPR8 Uncharacterized protein # K09949", 7.30e-64, 229]"
    toks2 = toks1[1].split(' # ')
    # ["UniRef100_A0LPR8 Uncharacterized protein", "K09949"]"
    toks2 = [toks1[0]] + [' # '.join(toks2[:-1]), toks2[-1]] + toks1[2:] #middle arr for case of >1 "#"
    # [1, "UniRef100_A0LPR8 Uncharacterized protein", "K09949", 7.30e-64, 229]"

    q, desc, ko, ev, score = toks2
    dtok = desc.split(' ')
    refid = dtok[0]             # UniRef100_A0LPR8
    desc = ' '.join(dtok[1:])   # Uncharacterized protein

    # ---------------------------------------------
    # the following likely won't need to be changed
    # it aggregates hits by query id (q)
    # and keeps track of a count and av scores

    if q in found:
        data = found[q]
    else:
        data = ([], set(), 0, 0, 0)

    dref, dko, dev, dscore, dcount = data
    dref.append(refid)
    dko.add(ko)
    dev = ((dev*dcount) + float(ev))/(dcount+1)
    dscore = ((dscore*dcount) + float(score))/(dcount+1)
    dcount += 1
    
    # (["UniRef100_A0LPR8"], ["K09949"], <av e-value>, <av bit-score>, <sum count>]"
    found[q] = (dref, dko, dev, dscore, dcount) 
    return True
#####################################################################################################

ROOT = os.environ['ROOT']
THREADS=6 # io limited, so maybe 6 is too many

# ref_desc = {}

def save(spath, fpath, found):
    # global ref_desc

    np.save(f'{spath}.summ', {'source': fpath,'results': found})
    # np.save(f'{spath}.descriptions', ref_desc)
    # ref_desc = {}

inpath = f'{ROOT}/annotated'
files = os.listdir(inpath)

def processOne(fname):
    fpath = f'{inpath}/{fname}'
    outPath = f'{ROOT}/summs/{fname}'
    if os.path.isfile(f"{outPath}.summ.npy"): return
    
    found = {}
    file = open(fpath)#, encoding='latin8')
    lnum = 0
    while 1:
        lnum+=1
        line = file.readline()
        if not line: break
        if line[0] == '#': continue
        parseLine(line, found)

    save(outPath, fpath, found)
    file.close()

os.system(f'mkdir -p {ROOT}/summs/')
with ProcessPoolExecutor(max_workers=THREADS) as executor:
    executor.map(processOne, files)
    executor.shutdown(wait=True)
# processOne(files[0])
print('done', len(files))