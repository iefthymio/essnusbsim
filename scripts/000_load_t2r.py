# %% -- Load T2R line optics and generate element DF
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

fin = opt_path / config.t2roptics
t2rline = xt.Line.from_json(fin)

print(f'''
      --- T2R optics file {fin} loaded
      
      T2R line length ......... {t2rline.get_length()}
      
      ''')

# %% --- get element DF 
_t2renv = t2rline.env
_t2renv.new('t2rend', xt.Marker)
t2rline.insert([
    _t2renv.place('t2rend', at=t2rline.get_length())
    ])

t2rline_df = t2rline.get_table(attr=True).to_pandas()
    
t2rline_df['kvalue'] = t2rline_df.apply(lambda x: hlp.get_kvalue(x), axis=1)

# %% --- get the survey information

t2rsrv_df = t2rline.survey().to_pandas()
t2rsrv_df = t2rsrv_df.rename(columns={'name':'name_srv'})
display(t2rsrv_df[t2rsrv_df.element_type != 'Drift'].head(40))

# %% -- join dataframes 

t2rline_df = t2rline_df.join(t2rsrv_df[['name_srv','X','Y','Z','theta','phi','psi']], how='outer')
assert t2rline_df.isna().any().any(), 'NaN values found in the dataframe' # there should be no NaN if dataframes of same length

# %% --- create elements DF
t2rline_elements_df = hlp.get_flukadf(t2rline_df, lineid='TL', verbose=True)

display(t2rline_elements_df)

# %% --- save dataframe to parquet file


t2rline_elements_df.to_parquet(output_path / "t2rline_elements.parquet")

print(f' --- T2R line element information saved in t2rline_elements.parquet file')
# %%
