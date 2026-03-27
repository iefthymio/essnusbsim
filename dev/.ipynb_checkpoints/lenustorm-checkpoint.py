# --- LEnuSTORM in Xsuite
#
#%%
import numpy as np

import xobjects as xo
import xtrack as xt

import matplotlib.pyplot as plt

#%%
env = xt.Environment()

MUON_MASS_EV = 105.7e6

env.particle_ref = xt.Particles(p0c=400e6, #eV
                                 q0=1, mass0=MUON_MASS_EV)

env.new('QFA', xt.Quadrupole, length = 0.125, k1 =  5.45022291277778148)
env.new('QDA', xt.Quadrupole, length = 0.25, k1 = -4.56255529153320527)
env.new('QFS', xt.Quadrupole, length = 0.125, k1 =  4.20157995314257704)
env.new('QDS', xt.Quadrupole, length = 0.25, k1 = -4.47765024083436547)
env.new('QDS_to_A1', xt.Quadrupole, length = 0.25, k1 = -4.50136419788634790)
env.new('QDS_to_A2', xt.Quadrupole, length = 0.25, k1 = -4.56741388890428279)
env.new('QFS_to_A1', xt.Quadrupole, length = 0.25, k1 = 4.82791218101006692)
env.new('D005', xt.Drift, length = 0.05)
env.new('D_sex', xt.Drift, length = 0.15)
env.new('D_stoA1', xt.Drift, length = 9.94409642653986126E-001)
env.new('DB', xt.Drift, length = 0.6)
env['a']= 0.6
env['b'] = np.pi/(6*2)
env['rho'] = 'a / b'
env.new('B', xt.Bend, length = 'a', h = '1/rho', k0 = '1/rho')


FODOA = env.new_line(
    name = 'fodoa',
    components = ['QFA', 'D_sex', 'D005', 'B', 'D005', 'D_sex', 'QDA', 'D_sex', 'D005', 'B', 'D005', 'D_sex', 'QFA'])

env.new('fodoa1', 'fodoa', mode='replica')
env.new('fodoa2', 'fodoa', mode='replica')
env.new('fodoa3', 'fodoa', mode='replica')
env.new('fodoa4', 'fodoa', mode='replica')
env.new('fodoa5', 'fodoa', mode='replica')
env.new('fodoa6', 'fodoa', mode='replica')

HALF_ARC = env.new_line(
    name = 'half-arc',
    components = ['fodoa1', 'fodoa2', 'fodoa3', 'fodoa4', 'fodoa5', 'fodoa6']
)

#HALF_ARC.get_table().show()

FODOS_to_A = env.new_line(
    name = 'FODOS_to_A', 
    components = ['QFS', 'D_stoA1', 'QDS_to_A1', 'D_stoA1', 
    'QFS_to_A1', 'D_stoA1', 'QDS_to_A2', 'D_stoA1', 'QFA'])

FODOS1 = env.new_line(
    name = 'fodos1', 
    components = ['QFS', 'D_sex', 'D005', 'DB', 'D005', 'D_sex', 
    'QDS', 'D_sex', 'D005', 'DB', 'D005', 'D_sex', 'QFS'])

STRAIGHT = env.new_line(
    name = 'straight',
    components = ['fodos1']*20
)

#FODOS_to_A.get_table().show()

HALF_RING = STRAIGHT + FODOS_to_A + HALF_ARC - FODOS_to_A + STRAIGHT

#HALF_RING.get_table().show()

FULL_RING = HALF_RING+HALF_RING

'''
straight = FODOS1+FODOS1

half_ring: line = (straight, FODOS_to_A, arc, -FODOS_to_A, straight)
full_ring: line = (2*half_ring)

Optimized parameters are:
 QFA[K1] =  5.45022291277778148E+000
 QDA[K1] = -4.56255529153320527E+000
 QFS[K1] =  4.20157995314257704E+000
 QDS[K1] = -4.47765024083436547E+000
 QDS_TO_A1[K1] = -4.50136419788634790E+000
 QDS_TO_A2[K1] = -4.56741388890428279E+000
 QFS_TO_A1[K1] =  4.82791218101006692E+000
 D_STOA1[L] =  9.94409642653986126E-001'''


## Attach a reference particle to the line (optional)
## (defines the reference mass, charge and energy)

#%%
## Choose a context
context = xo.ContextCpu()         # For CPU
# context = xo.ContextCupy()      # For CUDA GPUs
# context = xo.ContextPyopencl()  # For OpenCL GPUs

## Transfer lattice on context and compile tracking code
FULL_RING.build_tracker(_context=context)

## Compute lattice functions
tw = FULL_RING.twiss(method='4d')
print('TWISS')
tw.show()
# prints:
#
# name       s    betx    bety
# drift_0    0 3.02372 6.04743
# quad_0     2 6.04743 3.02372
# drift_1    2 6.04743 3.02372
# quad_1     3 3.02372 6.04743
# _end_point 3 3.02372 6.04743

#%%
## Build particle object on context
n_part = 200
particles = FULL_RING.build_particles(
                        x=np.random.uniform(-1e-3, 1e-3, n_part),
                        px=np.random.uniform(-1e-5, 1e-5, n_part),
                        y=np.random.uniform(-2e-3, 2e-3, n_part),
                        py=np.random.uniform(-3e-5, 3e-5, n_part),
                        zeta=np.random.uniform(-1e-2, 1e-2, n_part),
                        delta=np.random.uniform(-1e-4, 1e-4, n_part))
# Reference mass, charge, energy are taken from the reference particle.
# Particles are allocated on the context chosen for the line.

## Track (saving turn-by-turn data)
n_turns = 100
FULL_RING.track(particles, num_turns=n_turns,
              turn_by_turn_monitor=True)

## Turn-by-turn data is available at:
XS = FULL_RING.record_last_track.x
PXS = FULL_RING.record_last_track.px
# etc...

plt.plot(tw.s, tw.betx)
plt.plot(tw.s, tw.bety)

plt.show()

plt.scatter(XS, PXS)
plt.show()

FULL_RING.survey().plot()

plt.show()

#FULL_RING.to_json('line.json')
tw.to_pandas().to_csv('lenustorm-20241018.csv')

# Load from json
#line_2 = xt.Line.from_json('line.json')

#print(tw)
# Alternatively the to_dict method can be used, which is more flexible for
# example to save additional information in the json file
'''
#Save
dct = line.to_dict()
dct['my_additional_info'] = 'Important information'
with open('line.json', 'w') as fid:
    json.dump(dct, fid, cls=xo.JEncoder)'''
# %%
