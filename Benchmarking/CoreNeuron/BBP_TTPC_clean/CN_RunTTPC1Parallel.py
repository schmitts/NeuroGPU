# -*- coding: utf-8 -*-
"""
Created on Mon Oct  5 14:10:54 2020

@author: bensr
"""
from neuron import h
from neuron.units import ms, mV
import matplotlib.pyplot as plt
from CN_TTPC1 import Cell
import sys
import logging
from neuron import coreneuron

#print("\n".join(sys.argv))
import numpy as np
cell_to_plot = 0
param_list = np.loadtxt('./params/params.csv')
#ncell = len(param_list)
ncell = int(sys.argv[4])
#ncell = 8
pc = h.ParallelContext()
gids = range(pc.id(), ncell,pc.nhost()) # round robin
#print(f'the mpi_id is {pc.id()} and gids are {gids}')
#logging.warning(f'Before celss: the mpi_id is {pc.id()} ')
cells = [Cell(gid) for gid in gids]
#logging.warning(f'After we have all celss: the mpi_id is {pc.id()} ')
h.dt = 0.1
ntimesteps = 3168
tstop = ntimesteps*h.dt
pc.set_maxstep(10 * ms)
# make sure to enable cache efficiency
h.cvode.cache_efficient(True)
h.cvode.active(False)
h.dt = 0.1
#logging.warning(f'only run is left: the mpi_id is {pc.id()} ')
#print(pc.dt())
def prun():    
    #logging.warning(f'Before run: the mpi_id is {pc.id()} ')
    h.finitialize(-65)
    h.tstop = tstop
    pc.psolve(tstop)
coreneuron.enable = True
prun()
pc.barrier()
all_volts = []
for curr_cell in cells:
    all_volts.append(curr_cell.return_v()) 


#logging.warning(f'Before killing the PC: the mpi_id is {pc.id()} ')
pc.done()
h.quit()
