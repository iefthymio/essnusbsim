#
# --- Support script for ESSnuSB TT line to LEnuSTORM
#

from pprint import pprint

import xobjects as xo
import xtrack as xt

from particle import Particle

import numpy as np
import pandas as pd

import scipy

import re

class DotDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for key, value in self.items():
            if isinstance(value, dict):
                self[key] = DotDict(value)  # Recursively convert nested dicts

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]
        
def line_from_points(p1, p2):
    _dd = np.subtract(p2, p1)
    _slope = _dd[1]/_dd[0]
    _intercept = p1[1] - _slope * p1[0]
    return _slope, _intercept

def distance_point_to_line(lpar, pp):
    ''' Distance of point (x0, y0) to line (y = a * x + b): d = abs(a*x0 - y0 + b)/sqrt(a**2 + 1)'''
    _aa = lpar[0]
    _cc = lpar[1]
    return np.abs(_aa * pp[0] -pp[1] + _cc)/ np.sqrt(_aa**2 + 1)        
    
def dipole_length_from_angle(angle, arclength):
    rcurv = arclength/angle
    return rcurv * np.sin(angle)

def rotation_matrix(theta):
    
    c = np.cos(theta)
    s = np.sin(theta)
    
    return np.array([[c, -s], [s, c]])
    #return np.array([[c, s], [-s, c]])

def create_transform(t_x, t_y, theta):
    
    translation = np.array([t_x, t_y])
    rotation = rotation_matrix(theta)
    
    transform = np.eye(3, dtype=float)
    transform[:2, :2] = rotation
    transform[:2, 2] = translation
    
    return transform

def apply_transform(transform, x):
    
    x_h = np.ones((x.shape[0] + 1, x.shape[1]), dtype=x.dtype)
    x_h[:-1, :] = x
    
    x_t = np.dot(transform, x_h)
    
    return x_t[:2] / x_t[-1]

def load_lenustrom_ring(fin):
    _dfy = pd.read_parquet(fin)
    return _dfy[['s_fr','s_srv','name_fr','name_srv','Z_cm','X_cm']].copy()

def compute_corner_from_front_center(center, width, height, angle):
    """Compute bottom-left corner of a rectangle given its front-center."""
    # Convert angle to radians
    rad = np.radians(angle)
    # Offset from center to bottom-left corner
    dx = -(width / 2) * np.cos(rad) + (height / 2) * np.sin(rad)
    dy = -(width / 2) * np.sin(rad) - (height / 2) * np.cos(rad)
    # Return adjusted position
    return center[0] + dx, center[1] + dy

def compute_corner_from_center(center, width, height, rad):
    """Compute bottom-left corner of a rectangle given its center."""
    # Convert angle to radians
    # rad = np.radians(angle)
    # Offset from center to bottom-left corner
    dx = -(width / 2) * np.cos(rad) + (height / 2) * np.sin(rad)
    dy = -(width / 2) * np.sin(rad) - (height / 2) * np.cos(rad)
    # Return adjusted position
    return center[0] + dx, center[1] + dy

class TTLINE:
    bend_iron_yoke_side = 0.30   # iron width in the dipoles beyond the aperture
        
    def __init__(self, attributes=None, layout_attr=None):
        # print(f'__init__ : {attributes=}')
        for kk, vv in attributes.items():
            # print(f' seattr: {kk} = {vv}')
            setattr(self, kk, vv)
        
        for kk, vv in layout_attr.items():
            # print(f' seattr: {kk} = {vv}')
            setattr(self, kk, vv)
 
        self.l_bend_tot = self.l_bend + 2*self.l_bend_end
        self.l_quad_tot = self.l_quad + 2*self.l_quad_end
        self.l_qfl_tot = self.l_qfl + 2*self.l_qfl_end
        
        self.line_segments = [self.trg_to_d1pivot,
                              np.sqrt((self.d2_pivot[0]-self.d1_pivot[0])**2 + (self.d2_pivot[1]-self.d1_pivot[1])**2),
                              np.sqrt((self.lenustorm_inj[0]-self.d2_pivot[0])**2  + (self.lenustorm_inj[1]-self.d2_pivot[1])**2)]
        self.line_length = np.sum(self.line_segments)
        
        self.ring_orientation, self.ring_offset = line_equation([self.lenustorm_inj[1], self.lenustorm_inj[0]],
                                                                [self.trg_to_lemond,0])
                                                                 
        self.ring_orientation_deg = self.ring_orientation*180/np.pi

        self.ring_nearest_approach = distance_point_to_line([self.lenustorm_inj[1], self.lenustorm_inj[0]],
                                                            [self.trg_to_lemond, 0],
                                                            [self.l_decay_tunnel, -self.w_decay_tunnel/2])
    

        self.d1dipole = self.create_dipole(abs(self.d1_angle))
        self.min_distance_to_quad = (self.d1dipole['width'] - self.d1dipole['deflection'])/2 * np.sin(abs(self.d1_angle/2))
        self.create_cells()
        self.elements = self.create_elements()
        return
    
    def create_dipole(self, angle):
        _dipole = {}
        _dipole['angle'] = angle
        _dipole['bending_radius'] = self.l_bend / angle
        _dipole['arc'] = 2 * _dipole['bending_radius'] * np.sin(angle/2)
        _dipole['deflection'] = _dipole['arc'] * np.sin(angle/2)
        _dipole['length'] = _dipole['bending_radius'] * np.sin(angle)
        _dipole['width'] = _dipole['deflection'] + 2*self.beam_size + 2*TTLINE.bend_iron_yoke_side
        _dipole['height'] = 1.5*self.beam_size + 2*TTLINE.bend_iron_yoke_side
        _dipole['aperx'] = _dipole['deflection'] + self.beam_size
        _dipole['apery'] = 1.2*self.beam_size
        _dipole['pivot'] = _dipole['bending_radius'] * np.tan(angle/2)
        return _dipole
        
    def create_cells(self):
        cell_length = self.line_segments[1]/4
        self.cell_length_min = self.l_bend_tot/2 + 2*self.l_quad_tot + self.l_qfl_tot/2 + 3*self.l_vac

        assert cell_length > self.cell_length_min, f' -- ERROR {cell_length=} is less than mimimum allowed {self.cell_length_min}'
        self.l_vac_adjusted = self.l_vac + (cell_length - self.cell_length_min)/3
        self.cell_length = cell_length
        return
    
    def create_elements(self):
        ''' element positions - center'''
        _elements = []
        
        # -- distances from FL center to the center of the active element (MAD-X)
        _pos1 = self.l_qfl_tot/2 + 1/2*self.l_quad_tot + self.l_vac_adjusted
        _pos2 = self.l_qfl_tot/2 + 3/2*self.l_quad_tot + 2*self.l_vac_adjusted

        _aa = self.d1_angle
        _zz = self.d1dipole['bending_radius']*np.tan(abs(_aa)/2)
        
        _scumm = 0
        _elements.append({'name' :'TARGET', 'type': 'marker', 'spos' : _scumm, 'coord' : [0, 0], 'angle' : 0.0})
        _scumm = self.d1_pivot[1] - _zz
        _elements.append({'name' : 'MB1', 'type': 'bend', 'spos': _scumm + self.l_bend/2, 
                          'coord': [ 0, _scumm + self.d1dipole['length']/2], 'angle' : 0.0})
        
        _sfl1 = _scumm + self.l_bend + self.cell_length - _zz
        _bpos = self.cell_length - _pos2
        _elements.append({ 'name' :'QF1', 'type': 'quad', 'spos' : _sfl1 - _pos2, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = self.cell_length - _pos1
        _elements.append({ 'name' :'QD1', 'type': 'quad', 'spos' : _sfl1 - _pos1, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = self.cell_length
        _elements.append({ 'name' :'QFL1', 'type': 'fquad', 'spos' : _sfl1        , 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = self.cell_length + _pos1
        _elements.append({ 'name' :'QD2', 'type': 'quad', 'spos' : _sfl1 + _pos1, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = self.cell_length + _pos2
        _elements.append({ 'name' :'QF2', 'type': 'quad', 'spos' : _sfl1 + _pos2, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
  
        _sfl2 = _sfl1 + 2*self.cell_length
        _bpos = 3*self.cell_length - _pos2
        _elements.append({ 'name' :'QF3', 'type': 'quad', 'spos' : _sfl2 - _pos2, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle': _aa})
        _bpos = 3*self.cell_length - _pos1
        _elements.append({ 'name' :'QD3', 'type': 'quad', 'spos' : _sfl2 - _pos1, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = 3*self.cell_length
        _elements.append({ 'name' :'QFL2', 'type': 'fquad', 'spos' : _sfl2        , 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = 3*self.cell_length + _pos1
        _elements.append({ 'name' :'QD4', 'type': 'quad', 'spos' : _sfl2 + _pos1, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle' : _aa})
        _bpos = 3*self.cell_length + _pos2
        _elements.append({ 'name' :'QF4', 'type': 'quad', 'spos' : _sfl2 + _pos2, 
                          'coord': [self.d1_pivot[0] + _bpos*np.sin(_aa), self.d1_pivot[1] + _bpos*np.cos(_aa)], 'angle': _aa})

        _scumm = _sfl2 + self.cell_length - _zz
        _elements.append({'name' : 'MB2', 'type': 'bend', 'spos': _scumm + self.l_bend/2, 
                          'coord': [ self.d2_pivot[0], self.d2_pivot[1] + _zz - self.d1dipole['length']/2], 'angle' : 0.0}) 
            
        _scumm += self.l_bend + (self.lenustorm_inj[1]-self.d2_pivot[1]) - _zz
        _elements.append({'name' : 'INJ', 'type': 'marker', 'spos': _scumm, 
                          'coord': [ self.d2_pivot[0], self.d2_pivot[1] + (self.lenustorm_inj[1]-self.d2_pivot[1])], 'angle' : 0.0})    
        return _elements
        
    @classmethod
    def build_line_from_inj_point(cls, injpoint=(-14.5, 15), params=None, lparams=None):
        print(f' build_line_from_end_point : {injpoint=}')
        
        _x_inj, _z_inj = injpoint
        d2toinj_x, d2toinj_z = params['d2pivot_to_inj']
        trgtod1_z = params['trg_to_d1pivot']
        
        tan_theta = (_x_inj - d2toinj_x)/(_z_inj - d2toinj_z - trgtod1_z)
        
        params.update({'lenustorm_inj': injpoint,
                       'd2_pivot' : (_x_inj - d2toinj_x,_z_inj - d2toinj_z),
                       'd1_angle': np.atan(tan_theta),
                       'd1_angle_deg' : np.atan(tan_theta)*180/np.pi,
                       'd1_pivot' : (0, params['trg_to_d1pivot']),
                       'method' : f'from lenusotrm injection point coordinates ({injpoint} [m])'
                       })
        return cls(params, lparams)

    @classmethod
    def build_line_from_angle_and_displacement(cls, angle_deg=-54.0, xdisp=-12.5, params=None, lparams=None):
        print(f' build_line_from_angle_and_displacement : {angle_deg=}, {xdisp=}, {params=}')

        angle_rad = angle_deg*np.pi/180
        _d2pivot = (xdisp, params['trg_to_d1pivot']+ xdisp/np.tan(angle_rad))
        
        params.update({'d1_angle_deg': angle_deg,
                       'd1_angle' : angle_rad,
                       'd1_pivot' : (0, params['trg_to_d1pivot']),
                       'd2_pivot' : _d2pivot,
                       'lenustorm_inj' : (_d2pivot[0] + params['d2pivot_to_inj'][0],
                                          _d2pivot[1] + params['d2pivot_to_inj'][1]),
                       'method' : f'from angle ({angle_deg}[deg]) and lateral displacement ({xdisp}[m])'
                       })
        return cls(params, lparams)

    def __repr__(self):
        return "\n".join([f"{key}: {value}" for key, value in self.__dict__.items()])

    def dmpattributes(self):
        return print(json.dumps(self.__dict__, indent=4))
        
    def get_points(self):
        _xv = [0, self.d1_pivot[0], self.d2_pivot[0], self.lenustorm_inj[0]]
        _zv = [0, self.d1_pivot[1], self.d2_pivot[1], self.lenustorm_inj[1]]
        return _xv, _zv
    
    def display(self):
        for i in vars(self):
            vv = vars(self)[i]
            print (f" {i.ljust(30,'.')} {vars(self)[i]}")
            
            
            
def particle_beta_gamma(name, pmom_gev):
    _part = Particle.from_name(name) 
    _mass = _part.mass*1.0e-3 # convert from MeV to GeV
    _bgamma = pmom_gev/_mass
    _gamma = np.sqrt(_bgamma**2+1)
    _beta = _bgamma/_gamma
    return _beta, _gamma