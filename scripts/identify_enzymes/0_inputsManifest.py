from  glob import glob
import os

################################################################################################
# adapt to use your paths
INPUTS = [
    '<path to gtdbtk results>/*.gtdbtk/identify/intermediate_results/marker_genes/bin.*/bin.*_protein.faa',
]
################################################################################################

ROOT = os.environ['ROOT']

try: os.mkdir(ROOT)
except: pass
with open(f'{ROOT}/inputs.manifest', 'w') as man:
    for inp in INPUTS:
        for path in glob(inp):
            man.write(path+'\n')
