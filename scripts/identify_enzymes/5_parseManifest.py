import os

################################################################
# no adaptation required
################################################################

ROOT = os.environ['ROOT']
RUN=os.environ['RUN']

man = open(f'{ROOT}/run{RUN}.manifest')
tsv = open(f'{ROOT}/tables/manifest.tsv', 'w')
tsv.seek(0)
tsv.write(f'FileID\tPath\n')
while 1:
    line = man.readline()
    if not line: break
    if "--------------------------------------------------" in line: continue
    if len(line) < 2: continue
    toks = line.split(' ')
    fid, path = toks[0], ' '.join(toks[1:])
    tsv.write('\t'.join((fid, path)))

man.close()
tsv.truncate()
tsv.close()