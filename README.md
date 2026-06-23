# ESSnuSB+ Simulation 

Combined simulation of Target, T2R and LEnuSTORM structures

## Structure
```bash
project/

├── data/
│   ├── raw/        # the input .json files for the lines
│   ├── intermediate/  # parquet files with beam elements
│   └── inputs/     # generated FLUKA inp files
├── dev/            # development directory (obsolete)
├── docs/           # presentations and docs
├── fastsim/        # auxiliarry simulations 
├── notebooks/      # exploration notebooks for geometry build and testing
├── reports/        # html 
├── run/            # the main flair file
├── scripts/        # automation scripts to run for CI
├── src/            # beam optics and FLUKA files. FLAIR should be executed from this directory
├── tests/          # test of scripts

```

After download, you need to install it in your python environment using `pip install -e .`

## Running FLUKA

FLUKA should be executed in the **run** directory, doing the steps:
1 - copy the .inp files from te data/inputs
2.- run FLAIR using the **essnusbsim.flair** 

Note: the run ditectory is not sync with the github repository. 

## Optics files

### T2R line: 
    - **20251216-t2r.json** : latest version with injection to NUSTORM 
    - 20250922-t2r-line.json
    - 2025.08.07 : transfer-line-1050.json

### nuSTORM ring:
    - ring-mb3.json 
    - one-alternating-bend-ring600.json

## Script to generate the FLUKA Simulation Input

- **dev/generate_fluka.ipynb** : basic notebook file
    Input : beam files (optics) from the src direcory.
    Output: FLUKA output files *.inp in the same directory
    Status: see comments directly in the file

- **cp_inp_files.sh** : script to copy the new files from the dev directory to the src directory main one where the basic FLUKA/FLAIR project files are. 


## Automation CI integration

The files in `.github/workflows/ci.yml`

Runs pipeline scripts to generate new input files at each commit. 

Note : it runs only on [main] branch