# Install pipeline
## 1) Install snakemake and cookiecutter in a new environment
```
conda create -n snakemake python=3.9 cookiecutter snakemake
```

## 2 Clone repository
```
git clone 
```

## 3) Make a cluster profile
See the example below to make a SLURM profile

# Make a SLURM Profile
## 1) Make profile from cookiecutter template

To receive emails with jobs or finished or an error occurs replace `mail-user=account@email.com` with your email address. If you do not want emails, leave `sbatch_defaults []:` blank.

```
cookiecutter https://github.com/Snakemake-Profiles/slurm.git
profile_name [slurm]: slurm
sbatch_defaults []: mail-user=account@email.com mail-type=END,FAIL
cluster_sidecar_help: [Use cluster sidecar. NB! Requires snakemake >= 7.0! Enter to continue...]
Select cluster_sidecar:
1 - yes
2 - no
Choose from 1, 2 [1]:
cluster_name []:
cluster_config_help: [The use of cluster-config is discouraged. Rather, set snakemake CLI options in the profile configuration file (see snakemake documentation on best practices). Enter to continue...]
cluster_config []:
```

## 2) Edit profile config `slurm/config.yaml`

Add default resources, for example:
``` 
restart-times: 1
jobscript: "slurm-jobscript.sh"
cluster: "slurm-submit.py"
cluster-status: "slurm-status.py"
cluster-sidecar: "slurm-sidecar.py"
cluster-cancel: "scancel"
max-jobs-per-second: 1
max-status-checks-per-second: 10
local-cores: 1
latency-wait: 60

# Example resource configuration
default-resources:
  - runtime=60
  - mem_mb=8000
  - tmpdir="/scratch"
```

## 2) Move the profile to the correct location 
```
mkdir ~/.config/snakemake
mv slurm ~/.config/snakemake/
```

# Running pipeline
Replace `N` with number of sections defined in the config file. 

```
snakemake --configfile ../config/config.yaml --profile slurm --use-conda -j N
```
