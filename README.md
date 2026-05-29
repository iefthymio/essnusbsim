# ESSnuSB+ Simulation 

Combined simulation of Target, T2R and LEnuSTORM structures

# Structure
```bash
project/

├── data/           # input files (.json) for the TL and NUSTORM 
├── dev/            # where to generate the FLUKA input files
├── docs/           # presentations and docs
├── fastsim/        # auxiliarry simulations 
├── notebooks/      # exploration notebooks for geometry build and testing
├── reports/        # html 
├── run/            # what to download and run
├── scripts/        # automation scripts to run for CI
├── src/            # beam optics and FLUKA files. FLAIR should be executed from this directory
├── tests/          # test of scripts


```

## Automation CI integration

The files in `.github/workflows/ci.yml`

Runs pipeline scripts to generate new input files at each commit. 

Note : it runs only on [main] branch


## Script to generate the FLUKA Simulation Input

- **dev/generate_fluka.ipynb** : basic notebook file
    Input : beam files (optics) from the src direcory.
    Output: FLUKA output files *.inp in the same directory
    Status: see comments directly in the file

- **cp_inp_files.sh** : script to copy the new files from the dev directory to the src directory main one where the basic FLUKA/FLAIR project files are. 

