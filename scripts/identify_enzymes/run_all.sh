export ROOT='<specify output folder>'   # ex: '../cyano_enzymes'
export RUN='<give an arbitrary run id>' # ex: '1'

################################################################################################
# this script generates tables that describe identified proteins and links to them to 
# an associated metacyc enzyme if applicable  

python 0_inputsManifest.py
python 1_diamond.py
python 2_parseBlast.py
python 3_toBCID.py
python 4_toTable.py
python 5_parseManifest.py
