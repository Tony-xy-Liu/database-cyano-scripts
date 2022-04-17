import numpy as np
import os
from concurrent.futures import ProcessPoolExecutor

################################################################
# no change required, but please run the notebook at ../metacyc
# it will generate numpy dictionaries representing the metacyc pgdb 
################################################################

METACYC = './metacyc'

ROOT = os.environ['ROOT']
THREADS=6# (["UniRef100_A0LPR8"], ["K09949"], <av e-value>, <av bit-score>, <sum count>]"

def dictAppend(d:dict, k, v):
    if k in d:
        arr = d[k]
        arr.append(v)
    else:
        d[k] = [v]

def npload(path:str):
    if not path.endswith('.npy'): path = path+'.npy'
    return np.load(path, allow_pickle=True).item()

def makeRev(mapping, revKey, parser):
    rev = {}
    for k, v in mapping.items():
        if revKey not in v: continue
        for val in v[revKey]:
            parsed = parser(val)
            if type(parsed) == list:
                [dictAppend(rev, p, k) for p in parsed]
            else:
                dictAppend(rev, parsed, k)
    return rev

def passfn(x):
    return x

def viewDict(d, i=0):
    k = list(d.keys())[i]
    return k, d[k]

proteins = npload(METACYC+'proteins_uniprot')
rev_prot = makeRev(proteins, 'DBLINKS', lambda x: x[1])
enzrxns = npload(METACYC+'enzrxns')
rev_enz = makeRev(enzrxns, 'ENZYME', passfn)
reactions = npload(METACYC+'reactions')
rev_rxn = makeRev(reactions, 'ENZYMATIC-REACTION', passfn)

def toBioCyc(summPath):
    RK = 'results'
    UNIREF_PRE = 'UniRef100_'
    raw = np.load(summPath, allow_pickle=True).item()
    
    mps = {}
    for qk, entry in raw[RK].items():
        refs, kos, ev, score, count = entry
        for ref in refs:
            if not ref.startswith(UNIREF_PRE): continue
            ref = ref.replace(UNIREF_PRE, '')
            if ref in rev_prot: [dictAppend(mps, p, qk) for p in rev_prot[ref]]

    def link(keys, mapping):
        newLink = {}
        for k in keys:
            if k in mapping: [dictAppend(newLink, e, k) for e in mapping[k]]
        return newLink

    menz = link(mps, rev_enz)
    mrxns = link(menz, rev_rxn)

    return mrxns, menz, mps, raw

links = []

files = os.listdir(f'{ROOT}/summs')
os.system(f"mkdir -p {ROOT}/trace/")
print(f'to parse: {len(files)}')

def processOne(summ):
    outpath = f"{ROOT}/trace/{summ.replace('.tsv.summ', '')}"
    if os.path.isfile(outpath): return
    r, e, p, _ = toBioCyc(f'{ROOT}/summs/{summ}')
    np.save(outpath, (summ, r, e, p))

with ProcessPoolExecutor(max_workers=THREADS) as executor:
    executor.map(processOne, files)
    executor.shutdown(wait=True)

print('done to biocyc id', len(files))