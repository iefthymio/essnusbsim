# T2R and LEnuSTORM Simulation

ESSnuSB+ Simulation Studies for the LEnuSTORM stage

# Structure
```bash
project/
├── fluka0/         # initial FLUKA simulation code for target and decay pipe
├── pprod/          # FLUKA files for particle production out of the target
├── raytrace_cpp/   # tracking code developed for LAGUNA-LBNO CN2PY design studies
├── src/            # beam optics and FLUKA files. FLAIR should be executed from this directory
├── dev/            # where to generate the FLUKA input files
├── refinp/         # historical files fromp past simulations for reference
├── fastsim/        # auxiliarry simulations 
├── run/            # obsolete dir - should be deleted
└── README.md
└── InitPlots.py
└── README_init.md  # initial README kept for reference 
└── FLUKA-sim.pptx  # help file for the FLUKA simulation of the beam lines
```

## Script to generate the FLUKA Simulation Input

- **dev/generate_fluka.ipynb** : basic notebook file
    Input : beam files (optics) from the src direcory.
    Output: FLUKA output files *.inp in the same directory
    Status: see comments directly in the file

- **cp_inp_files.sh** : script to copy the new files from the dev directory to the src directory main one where the basic FLUKA/FLAIR project files are. 

