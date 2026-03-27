# 
# Python Initialisation File for Plots
#
# Should be called from Jupyter Notebooks or in SWAN at first line with the command:
#
# %run /eos/home-e/efthymio/InitPlots.py
#
__version__ = '1.02 - 07.03.2023 (IE)'
print (f'\n>>> Running InitPlots.py - Version : {__version__}')
#
# -- I need this to avoid problems with the display variable when running in SWAN
# get_ipython().magic('matplotlib inline')
# get_ipython().magic('matplotlib notebook')

# import sys
# sys.path.append('/eos/user/e/efthymio/Projects/LHCLumi/LHCLumiAnalysis/')
# for p in sys.path:
#     print (p)

# from selectors import EpollSelector
import matplotlib

import matplotlib.patches as patches
import matplotlib.dates as md
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)

try:
    import seaborn as sns
except:
    print('seaborn not available - need to install it with pip ')

# -- for nice plotting

class MyPlots():
    def __init__(self, outpath='./', savefig=False, verbose=False):
        self.outpath = outpath
        self.savefig = savefig
        self.verbose = verbose

    def get_outpath(self):
        return self.outpath
    
    def set_outpath(self, outpath):
        self.outpath = outpath
        return
    
    def get_savefig(self):
        return self.savefig

    def set_savefig(self, savefig):
        self.savefig = savefig
        return
    
    def set_verbose(self, verbose):
        self.verbose = verbose
        return

    def configPlots(self, style): 
        ''' configure matplotlib figures '''
        print (f'---- running configPlots function ')
        plt.rcParams['axes.grid']=False
        plt.rcParams['axes.facecolor']='none'
        plt.rcParams['axes.grid.axis']='both'
        plt.rcParams['axes.spines.bottom']=True
        plt.rcParams['axes.spines.left']=True
        plt.rcParams['axes.spines.right']=True
        plt.rcParams['axes.spines.top']=True

        # plt.rcParams
        # sns.set_style("white")  
        # sns.set_style("ticks")
        # sns.cmset_context("paper")
        # plt.rcParams['xtick.direction']='in'
        # plt.rcParams['ytick.direction']='in'

        # style = 'default'
        if style != '':
            plt.style.use(style)
        else:
            plt.style.use('default')

        labsize = 18
        labweight = 'normal'

        txtsize = 15
        legsize = 12
        titsize = 20

        tksize = 12
        tkdir = 'in'
        tkmajor = 5.0
        tkminor = 3.0

        lsize = 18
        fsize = 15
        tsize = 12
        tdir = 'in'
        major = 5.0
        minor = 3.0

        # plt.rcParams['text.usetex'] = True
        plt.rcParams['font.size'] = txtsize
        plt.rcParams['legend.fontsize'] = legsize
        plt.rcParams['xtick.direction'] = tkdir
        plt.rcParams['ytick.direction'] = tkdir
        plt.rcParams['xtick.major.size'] = tkmajor
        plt.rcParams['xtick.minor.size'] = tkminor
        plt.rcParams['ytick.major.size'] = tkmajor
        plt.rcParams['ytick.minor.size'] = tkminor

        plt.rcParams['xtick.labelsize'] = labsize
        plt.rcParams['ytick.labelsize'] = plt.rcParams['xtick.labelsize']
        plt.rcParams['axes.titlesize'] = plt.rcParams['xtick.labelsize']
        plt.rcParams['axes.labelweight'] = labweight
        plt.rcParams['axes.labelsize']=plt.rcParams['xtick.labelsize']
        plt.rcParams['legend.fontsize']=plt.rcParams['xtick.labelsize']

        plt.rcParams['figure.titlesize'] = titsize

        # matplotlib.rcParams.update({'font.size': 8*2})
        matplotlib.rc('font',**{'family':'serif'})

        # plt.rcParams['figure.figsize']=(7.5,4.7) # in inches
        # matplotlib.rcParams['figure.figsize']=(15,7.5)
        plt.rcParams['figure.figsize']=(15, 10) # in inches
        # matplotlib.rcParams.update({'font.size': 15})
        return

    #%config InlineBackend.figure_format = 'retina'

    def savFig2File(self, fig, fout, dpi=300):
        if self.savefig:
            fig.savefig(fout, dpi=dpi, bbox_inches='tight')
            if self.verbose :
                print ('>>> Plot saved to :',fout)
        return
    
    def fig2file(self, fig, fout, dpi=300):
        fig.savefig(f'{self.outpath}/{fout}', dpi=dpi, bbox_inches='tight')
        return
    
