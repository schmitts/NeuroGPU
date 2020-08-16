#!/bin/bash
#SBATCH --qos=regular
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --constraint=knl
#SBATCH --mail-user=zladd@berkeley.edu
#SBATCH --mail-type=ALL
#SBATCH --array 1-100

# I added this, is there some way to pass these in? probably not
CURRENTDATE=`date +%m_%d_%Y`
input="input.txt"
while IFS= read -r line
do
    IFS='=' read -ra inputs <<< "$line"
    name="${inputs[0]}"
    data="${inputs[1]}"
    printf -v $name "$data"
done < "$input"


echo "start-A "`hostname`" task="${job_sh}
echo  'cscratch='${CSCRATCH}
echo  'scratch='${SCRATCH}
echo SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}
echo SLURM_JOBID=${SLURM_JOBID}
srcDir=`pwd`

sleep 2

coreN=${srcDir}/'runs'/${model}_${peeling}_${CURRENTDATE}${custom}/'volts_sand'/${SLURM_ARRAY_JOB_ID}
arrIdx=${SLURM_ARRAY_TASK_ID}
wrkDir=${coreN}-${arrIdx}
echo 'my wrkDir='${wrkDir}
mkdir -p ${wrkDir}


dirToRun=run_volts_${model}_${peeling}


cp -rp 'run_volts'/${dirToRun} ${wrkDir}/


cd ${wrkDir}/${dirToRun}

echo inventore at start
pwd
ls -l *

export OMP_NUM_THREADS=1

srun -n 68 python run_stim_hdf5.py $arrIdx

# mv slurm log to final destination - it is alwasy a job-array
mv $srcDir/slurm-${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}.out .
