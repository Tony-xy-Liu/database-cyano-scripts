import os
import sys
from datetime import datetime

################################################################
# adapt to use your paths
DIAMOND="<path to diamond executable>/diamond"

UNIPROT="<path to uniprot db for diamond>/uniprot.dmnd"
# example .faa used to make the database for diamond
# the one we used also had kegg orthology numbers, but KOs are not
# required for this analysis
    # >sp|Q6GZS4|052L_FRG3G Uncharacterized protein 052L # K12408
    # MVKYVVTG...
    # >sp|Q92AT0|12OLP_LISIN 1,2-beta-oligoglucan phosphorylase # K21298
    # MTMLKEIK...
    # >sp|P48347|14310_ARATH 14-3-3-like protein GF14 epsilon # K06630
    # MENEREKQ...
################################################################

RUN=os.environ['RUN']
ROOT = os.environ['ROOT']
THREADS=12

INPUT_MANIFEST=f"{ROOT}/inputs.manifest"
OUTPUT_MANIFEST = f'{ROOT}/run{RUN}.manifest'
OUTPUT_DIR=f'{ROOT}/annotated'
COMMANDS_LOG = f'{ROOT}/run{RUN}.txt'

FORMAT='6 qseqid stitle evalue bitscore'

if not os.path.isdir(OUTPUT_DIR): os.system(f'mkdir {OUTPUT_DIR}')

def report(msg, rpath):
    if not os.path.isfile(rpath): os.system(f'touch {rpath}')
    with open(rpath, 'a') as rep:
        line = f'{" ".join([str(m) for m in msg]) if type(msg) == tuple else str(msg)}'
        if not line.endswith('\n'): line += '\n'
        rep.write(line)

report((datetime.now(), '-'*50), COMMANDS_LOG)
report((datetime.now(), '-'*50), OUTPUT_MANIFEST)

with open(INPUT_MANIFEST, 'r') as inmans:
    i = 0
    while True:
        i+=1
        inpath = inmans.readline()
        if not inpath: break

        if f"die{RUN}" in os.listdir(ROOT):
            report((datetime.now(), "killed"), COMMANDS_LOG)
            sys.exit()

        outpath=f'{OUTPUT_DIR}/{i}.tsv'
        if os.path.isfile(outpath):
            report(("skipping", outpath), COMMANDS_LOG)

        cmd = f'''{DIAMOND} blastp \
            -d "{UNIPROT}" \
            -q "{inpath}" \
            --outfmt {FORMAT} \
            -o "{outpath}" \
            -p {THREADS} \
            '''.replace("  ", "").replace('\n', '')
        # cmd = f"echo {fpath}"
        report((datetime.now(), cmd), COMMANDS_LOG)
        # print(cmd)
        os.system(cmd)
        
        with open(outpath, 'r+') as resultf:
            # remove garbage in id seq
            result = ['\t'.join([t[0].split('_')[-1]] + t[1:]) for t in [r.split('\t') for r in resultf.readlines()]]
            resultf.seek(0)
            resultf.writelines(result)
            resultf.truncate()
        report((i, inpath), OUTPUT_MANIFEST)