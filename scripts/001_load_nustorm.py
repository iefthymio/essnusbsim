# %% -- Load leNuSTORM rign optics and generate element DF
#

import numpy as np
import pandas as pd

import xobjects as xo
import xtrack as xt

import math

import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.patches as patches

try:
    get_ipython()  # exists only in IPython/Jupyter
    from IPython.display import display
except NameError:
    display = print

import essnusbsim.helpers as hlp

import re
import json
import yaml, pprint
# from dotdict import DotDict as dd

from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

data_path = BASE / "data" 
opt_path = BASE / "data" / "raw"
output_path = BASE / "data" / "intermediate"

paths = {
    "BASE": BASE,
    "data_path": data_path,
    "opt_path": opt_path,
    "output_path": output_path,
}

print("\n" + "=" * 80)
print(f"Starting {__file__}")
print("=" * 80 + "\n")

print("\nDefined paths:")
for name, value in paths.items():
    print(f"  {name:<15} {value}")


# %% --  load configuration

with open(f'{data_path}/essbeamsim.yaml','r') as fin:
    config = hlp.DotDict(yaml.safe_load(fin))
pprint.pprint(config)


# %% -- reload
from importlib import reload
reload(hlp)


# %% -- load optics

fin = opt_path / config.nustormoptics
fin = opt_path / 'one-alternating-bend_arc_fodo-600.json'
fin = opt_path / 'one-alternating-bend_matching_cell-S2A-600.json'
fin = opt_path / 'one-alternating-bend_straight_fodo-600.json'
nustorm = xt.Line.from_json(fin)

print(f'''
      --- nuSTORM optics file {fin} loaded
      
      nuSTORM ring length ......... {nustorm.get_length()}
      
      ''')

# %% --- get element DF 
if False : 
    _nustormenv = nustorm.env
    _nustormenv.new('t2rend', xt.Marker)
    nustorm.insert([
        _nustormenv.place('t2rend', at=nustorm.get_length())
        ])

nustorm_df = nustorm.get_table(attr=True).to_pandas()
    
nustorm_df['kvalue'] = nustorm_df.apply(lambda x: hlp.get_kvalue(x), axis=1)

# %% --- get the survey information

nustormsrv_df = nustorm.survey().to_pandas()
nustormsrv_df = nustormsrv_df.rename(columns={'name':'name_srv'})
display(nustormsrv_df[nustormsrv_df.element_type != 'Drift'].head(40))

# %% -- join dataframes 

nustorm_df = nustorm_df.join(nustormsrv_df[['name_srv','X','Y','Z','theta','phi','psi']], how='outer')
assert nustorm_df.isna().any().any(), 'NaN values found in the dataframe' # there should be no NaN if dataframes of same length

# %% --- create elements DF
nustorm_elements_df = hlp.get_flukadf(nustorm_df, lineid='TL', verbose=True)

display(nustorm_elements_df)

# %% --- save dataframe to parquet file


nustorm_elements_df.to_parquet(output_path / "nustorm_elements.parquet")

print(f' --- T2R line element information saved in nustorm_elements.parquet file')
# %%
