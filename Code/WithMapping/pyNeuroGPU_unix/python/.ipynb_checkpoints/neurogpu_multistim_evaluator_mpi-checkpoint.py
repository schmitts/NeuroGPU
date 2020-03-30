import numpy as np
import os
import subprocess
import shutil
import bluepyopt as bpop
from mpi4py import MPI

import struct
import time
import efel_ext
import matplotlib.pyplot as plt
import bluepyopt.deapext.algorithms as algo
from extractModel_mappings_linux import   allparams_from_mapping

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
print('My rank is ',rank)
params_table = '../Data/opt_table.csv'
exp_data = '../Data/exp_data/'
param_file ='../Data/gen.csv'
data_dir = '../Data/'
run_dir = '../bin/'
orig_volts_fn =  exp_data + './exp_data.csv'
vs_fn ='../Data/VHotP.dat'
times_file_path = '../Data/times.csv'
nstims = 4
plot_flg=False
target_volts = np.genfromtxt(orig_volts_fn)
times =  np.cumsum(np.genfromtxt(times_file_path,delimiter=','))
#times = times[:-1]


old_eval = algo._evaluate_invalid_fitness
def nrnMread(fileName):
    f = open(fileName, "rb")
    nparam = struct.unpack('i', f.read(4))[0]
    typeFlg = struct.unpack('i', f.read(4))[0]
    return np.fromfile(f,np.double)


class neurogpu_multistim_evaluator(bpop.evaluators.Evaluator):
    def __init__(self):
        """Constructor"""
        def read_with_genfromtxt(path, type=float, delim=None):
            r = np.genfromtxt(path, dtype=type, delimiter=delim)
            if np.shape(r) == ():
                return np.array([r.item()])
            return r
        super(neurogpu_multistim_evaluator, self).__init__()
        
        data = np.genfromtxt(params_table,delimiter=',',names=True)
        self.pmin = data[0]
        self.pmax = data[1]
        self.ptarget = data[2]
        
        params = []
        for i in range(len(self.pmin)):
            params.append(bpop.parameters.Parameter('p' + str(i), bounds=(self.pmin[i],self.pmax[i])))
        
        self.params = params
        
        #self.opt_stim_list = read_with_genfromtxt(opt_stim_name_list, str, ' ')
        # ['mean_frequency', 'adaptation_index', 'time_to_first_spike', 'mean_AP_amplitude', 'ISI values', 'spike_half_width']
        # ['voltage_base','steady_state_voltage_stimend','decay_time_constant_after_stim']
        
        
       
        self.objectives = [bpop.objectives.Objective('voltage_base_1'),\
                           bpop.objectives.Objective('AP_amplitude_1'),\
                           bpop.objectives.Objective('voltage_after_stim_1'),\
                           bpop.objectives.Objective('ISI values_1'),\
                           bpop.objectives.Objective('spike_half_width_1'),\
                           bpop.objectives.Objective('AHP_Depth_1'),\
                           bpop.objectives.Objective('chi_1'),\
                           
                           bpop.objectives.Objective('voltage_base_2'),\
                           bpop.objectives.Objective('AP_amplitude_2'),\
                           bpop.objectives.Objective('voltage_after_stim_2'),\
                           bpop.objectives.Objective('ISI values_2'),\
                           bpop.objectives.Objective('spike_half_width_2'),\
                           bpop.objectives.Objective('AHP_Depth_2'),\
                           bpop.objectives.Objective('chi_2'),\
                           
                           bpop.objectives.Objective('voltage_base_3'),\
                           bpop.objectives.Objective('AP_amplitude_3'),\
                           bpop.objectives.Objective('voltage_after_stim_3'),\
                           bpop.objectives.Objective('ISI values_3'),\
                           bpop.objectives.Objective('spike_half_width_3'),\
                           bpop.objectives.Objective('AHP_Depth_3'),\
                           bpop.objectives.Objective('chi_3'),\
                           
                           bpop.objectives.Objective('voltage_base_4'),\
                           bpop.objectives.Objective('AP_amplitude_4'),\
                           bpop.objectives.Objective('voltage_after_stim_4'),\
                           bpop.objectives.Objective('ISI values_4'),\
                           bpop.objectives.Objective('spike_half_width_4'),\
                           bpop.objectives.Objective('AHP_Depth_4'),\
                           bpop.objectives.Objective('chi_4')
                          
                           ]
        #self.toolbox.register("evaluate", self.evaluator.evaluate_with_lists)
    def my_evaluate_invalid_fitness(toolbox, population):
        '''Evaluate the individuals with an invalid fitness

        Returns the count of individuals with invalid fitness
        '''
        invalid_ind = [ind for ind in population if not ind.fitness.valid]
        invalid_ind = [population[0]] + invalid_ind 
        fitnesses = toolbox.evaluate(invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        return len(invalid_ind)
    def run_model(self,population,stim_ind):
        all_volts = []
        param_mat = np.array(population)
        if os.path.exists(vs_fn):
            os.remove(vs_fn)
        
        #os.chdir(model_dir)
        np.savetxt(param_file,param_mat,delimiter=' ')
        curr_psize = len(population)
        allparams = allparams_from_mapping(params_input=param_mat)
        #shutil.move(data_dir + 'AllParams.csv', run_dir + "/Data/AllParams.csv")
        #time.sleep(1)
        print('params are:')
        print(population[0])
        if os.path.exists(vs_fn):
            os.remove(vs_fn)
            #tim_ind +=1
        shutil.copy("../Data/Stim_raw" + str(stim_ind) + ".csv", run_dir + "../Data/Stim_raw.csv")
            #os.chdir(run_dir + '/x64/')
        print("call neurogpu6")
        subprocess.call('../bin/neuroGPU')
        #file exists
        volts = nrnMread(vs_fn)
        os.remove("../Data/Stim_raw.csv")
        Nt = int(len(volts)/curr_psize)
        shaped_volts = np.reshape(volts, [curr_psize, Nt])
        if (plot_flg is True):
            plt.plot(shaped_volts[0],'r')
            plt.plot(target_volts[stim_ind-1][:],'black')
            plt.show()
            #ll_volts.append(shaped_volts)
            
        return  shaped_volts
   
    


    def evaluate_with_lists(self,param_values):
        all_scores = []
        for stim_ind in range(4):
            stim_ind+=1
            volts = self.run_model(param_values,stim_ind);
            scores = efel_ext.eval([target_volts[stim_ind]],volts,times)
            all_scores.extend(scores)
                
        #data_volts_list = run_model(param_values, self.opt_stim_list)
        #score = efel_ext.eval(self.opt_stim_list, self.target_volts_list, data_volts_list)
        # This should be a list
        #return score
        
        return all_scores



algo._evaluate_invalid_fitness =neurogpu_multistim_evaluator.my_evaluate_invalid_fitness







