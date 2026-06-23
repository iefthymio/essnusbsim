#
# --- Support script for ESSnuSB TT line to LEnuSTORM
#

from pprint import pprint

import xobjects as xo
import xtrack as xt

from particle import Particle

import numpy as np
import pandas as pd

import py4madx as pm

import scipy

import matplotlib 
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from . import helpers as hlp

import re

def plot_layout(trline, ringdf, layout_params):

    fig, ax = plt.subplots(figsize=(20, 10))

    # --- plot infrastructure
    
    x_width = layout_params['w_decay_tunnel']/2*100
    r_decay = layout_params['r_decay_pipe']*100
    z_length = layout_params['l_decay_tunnel']*100
    z_dump = (z_length - 1000)
    
    
    xtunnel = [0, -x_width, -x_width, x_width, x_width, 0]
    rdecay = [0, -r_decay, -r_decay, r_decay, r_decay, 0]
    ztunnel = [0, 0, z_length, z_length, 0, 0]
    zpipe = [0, 0, z_dump, z_dump, 0, 0]

    # plt.plot(ztunnel, xtunnel, 'o-', color='black')
    ax.fill(ztunnel, xtunnel, color='brown')
    ax.fill(zpipe, rdecay, color='cyan')
    ax.plot(layout_params['trg_to_lemond']*100, 0, 'o', color='red', label='LEMMOND')

    to_lemond = (layout_params['trg_to_lemond']+20)*100
    ax.arrow(0, 0, to_lemond, 0, shape='full', linewidth=2, linestyle='--', 
             length_includes_head=True, head_width=0.5, head_length=8, color='blue')
    
    # --- plot transfer line
    
    xx1, zz1 = trline.get_points()
    ax.plot(np.array(zz1)*100, np.array(xx1)*100, '*-', color='red', label='transfer line')

    # --- plot the LEnuSTORM ring
    
    _inj_point = trline.__getattribute__("lenustorm_inj")
    _angle = trline.__getattribute__("ring_orientation")
    
    ring_coord_transform = hlp.create_transform(_inj_point[1]*100, _inj_point[0]*100, _angle)
    print(ring_coord_transform)

    ring_2d = ringdf[['Z_cm','X_cm']].to_numpy()
    transformed = hlp.apply_transform(ring_coord_transform, np.array(ring_2d).T)
    ringdf['Z_wc'] = transformed[0]
    ringdf['X_wc'] = transformed[1]

  
    # ringdf.plot('Z_cm','X_cm', ax=ax)
    # ax.plot(ringdf.iloc[0].Z_cm, ringdf.iloc[0].X_cm, '*', color='red')

    ringdf.plot('Z_wc', 'X_wc', ax=ax)
    ax.plot(ringdf.iloc[0].Z_wc, ringdf.iloc[0].X_wc, '*', color='green')
    
    _endss = ringdf[ringdf.theta == 0].iloc[-1]
    print(_endss.Z_wc, _endss.X_wc, layout_params['trg_to_lemond']*100)
    ax.plot([_endss.Z_wc, layout_params['trg_to_lemond']*100], [_endss.X_wc, 0], linestyle='--', lw=1, color='green')
    
    ax.set_title(trline.__getattribute__('method'))
    # plt.title(f'LEnuSTORM ring ($z_{{inj}}$ = {lenustorm_inj_z} [cm], $x_{{inj}}$ = {lenustorm_inj_x} [cm])')
    # ax.plot(transformed[0], transformed[1])
    # ax.plot(transformed[0][0], transformed[1][0], '+', color='green')
    ax.axis('equal')
    ax.grid(which='major', color='r', linestyle='-', alpha=0.5)
    ax.grid(which='minor', color='r', linestyle='--', alpha=0.2)
    ax.minorticks_on()
    ax.legend()
    
    
    return fig

def plot_ttline(theline):
        
    fig, ax = plt.subplots(figsize=(15,10))

    for el in theline.elements:
        _name = el['name']
        _type = el['type']
        if _type == 'bend':
            _length = theline.l_bend
            _length_tot = theline.l_bend_tot
            _width = theline.d1dipole['width']
            _edgecolor = 'blue'
            _facecolor = 'lightblue'
        elif _type == 'quad' :
            if _name in ['QFL1', 'QFL2']: 
                _length = theline.l_qfl
                _length_tot = theline.l_qfl_tot
                _width = theline.l_qfl_w
                _edgecolor = 'magenta'
                _facecolor = 'yellow'
            else:
                _length = theline.l_quad
                _length_tot = theline.l_quad_tot
                _width = theline.l_quad_w
                _edgecolor = 'orange'
                _facecolor = 'green'
        elif _type == 'marker':
            if _name == 'TARGET':
                _length = 0.78
                _length_tot = _length
                _width = 0.02
                _edgecolor = 'black'
                _facecolor = 'grey'
            else:
                _length = 0.10
                _length_tot = _length
                _width = 0.10
                _edgecolor = 'black'
                _facecolor = 'grey'
        
        print(f" -- {el['name']} : xy ={el['coord'][1]:.3f}, {el['coord'][0]}  {el['angle']}")
        _center = (el['coord'][1], el['coord'][0])

        bottom_left = hlp.compute_corner_from_center(_center, _length_tot, _width, el['angle'] )
        # print(f'\t --- {bottom_left=}')
        ax.add_patch(
            patches.Rectangle(
                xy=bottom_left, width=_length_tot, height=_width, angle=el["angle"]*180/np.pi,
                edgecolor='lightgrey', facecolor='brown', linewidth=1, linestyle='--'
            )
        )
        bottom_left = hlp.compute_corner_from_center(_center, _length, _width, el['angle'] )
        # print(f'\t --- {bottom_left=}')
        ax.add_patch(
            patches.Rectangle(
                xy=bottom_left, width=_length, height=_width, angle=el["angle"]*180/np.pi,
                edgecolor=_edgecolor, facecolor=_facecolor, linewidth=1
            )
        )
        
        ax.plot(*_center, "ro")  # Center marked as a red dot

    pxx, pzz = theline.get_points()
    
    pxx.insert(len(pxx)-1, pxx[len(pxx)-2])
    pzz.insert(len(pzz)-1, 0.5*(pzz[-2]+pzz[-1]))
    ax.plot(pzz[:-1], pxx[:-1], '*-', linewidth=0.7, color='green')
    ax.plot(pzz[-2:], pxx[-2:], '*--', linewidth=0.7, color='olive')

    # ax.set_xlim(0, 18)
    # ax.set_ylim(0, 5)
    ax.set_aspect('equal')

    ax.set_title(theline.__getattribute__('method'))
    # Show the plot
    ax.grid(which='major', color='k', linestyle='-', alpha=0.5)
    ax.grid(which='minor', color='r', linestyle='--', alpha=0.2)
    # ax.grid('minor', color='g', linestyle='--')
    ax.minorticks_on()
    plt.show()
    return fig

def plot_optics(dftwiss, bim, title='', ymax=[], yticks='', ymaxdisp=[-1,3]):
    ''' Plot beam optics for the input twiss '''

    beamid = bim.lower()
    df_beam = dftwiss[dftwiss['beam']==bim]

    fig, axes = plt.subplots(nrows=2, ncols=1, sharex='col', 
                             gridspec_kw={'height_ratios': [1,4]},
                             figsize=(25,10))
    fig.set_tight_layout({'pad':0.1, 'h_pad':0.1})

    # -- head plot with lattice info
    ax1 = axes[0]
    ax1.plot(df_beam['s'],0*df_beam['s'],'k')
    fstring = f' Initial :$\\beta_x$={dftwiss.iloc[0].betx:.2f}, $\\beta_y$={dftwiss.iloc[0].bety:.2f}'
        
    ax1.text(0.6, 1.02, fstring, fontsize=12, transform=ax1.transAxes)

    DF=df_beam[(df_beam['keyword']=='quadrupole')]
    for i in range(len(DF)):
        aux=DF.iloc[i]
        pm.plotLatticeSeries(ax1, aux, height=aux.k1l, v_offset=aux.k1l/2, color='r')

    color = 'red'
    ax1.set_ylabel('1/f=K1L [m$^{-1}$]', color=color)  # we already handled the x-label with ax1
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid()
    ax1.set_ylim(-.05,.05)
    ax1.set_title(title, loc='center', fontsize=18)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'blue'
    ax2.set_ylabel('$\\theta$=K0L [mrad]', color=color)  # we already handled the x-label with ax1
    ax2.tick_params(axis='y', labelcolor=color)

    DF=df_beam[(df_beam['keyword']=='rbend')]
    for i in range(len(DF)):
        aux=DF.iloc[i]
        pm.plotLatticeSeries(ax2, aux, height=aux.angle*1000, v_offset=aux.angle/2*1000, color='b')

    DF=df_beam[(df_beam['keyword']=='sbend')]
    for i in range(len(DF)):
        aux=DF.iloc[i]
        pm.plotLatticeSeries(ax2, aux, height=aux.angle*1000, v_offset=aux.angle/2*1000, color='b')
    ax2.set_ylim(-15,15)
    
    # -- bottom plot with optics data
    ax0 = axes[1]

    ax0.plot(df_beam['s'],df_beam['betx'],'b', label='$\\beta_x$')
    ax0.plot(df_beam['s'],df_beam['bety'],'r', label='$\\beta_y$')
    ax0.legend(loc='upper right')
    ax0.set_ylabel('$\\beta$-functions [m]')
    ax0.set_xlabel('s [m]')
    # ax0.axvline(df_beam.loc[ip].s, ls='--', color='black')
            
    ax3 = ax0.twinx()   # instantiate a second axes that shares the same x-axis
    
    pdx,pdy = ax3.plot(df_beam['s'], df_beam['dx'], '-', df_beam['s'],df_beam['dy'], '--', color='orange')
    ax3.tick_params(axis='y', labelcolor='orange')
    ax3.set_ylabel('$D_{x,y}$ [m]', color='orange')  # we already handled the x-label with ax1
    ax3.legend([pdx, pdy], ['$D_x$','$D_y$'], loc='upper left')
    ax3.set_ylim(ymaxdisp)

    ax0.grid()
    if ymax :
        ax0.set_ylim(ymax[0])
        # ax3.set_ylim(ymax[1])

    if yticks:
        start, end = ax0.get_ylim()
        ax0.yaxis.set_ticks(np.arange(start, end, yticks))


    #fig.savefig('/cas/images/LHCB1OpticsRing.pdf')
    return fig
