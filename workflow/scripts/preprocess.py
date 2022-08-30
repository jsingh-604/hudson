from pre import utils
from pre import image_analysis as ia
from os.path import join, isdir
from os import makedirs
#from utils.utils import get_cluster
from utils import get_cluster
from dask.distributed import Client, wait
import dask
from pathlib import Path
import yaml



experiment_config = utils.get_config(snakemake.input[0])
exp_dir = snakemake.config['experiment_directory']
image_path = snakemake.config.get('image_path',experiment_config['experiment']['image path'])
image_path = join(exp_dir, image_path)

section_name = snakemake.params.section

logger = utils.get_logger(logname = section_name, filehandler = snakemake.log)

image = ia.get_HiSeqImages(image_path = image_path, common_name = section_name,
                           logname = f'{section_name}.image')

# Start dask cluster
# specify default worker options in ~/.config/dask/jobqueue.yaml
winfo = snakemake.config.get('resources',{}).get('dask_worker',{})
cluster = get_cluster(**winfo)
logger.info(cluster.new_worker_spec())
logger.info(cluster.dashboard_link)
ntiles = int(len(image.im.col)/2048)
min_workers = max(1,2*ntiles)
max_workers = 2*ntiles*ntiles

# Print out info about section
logger.info('machine::', image.machine)
logger.info('image path::',image_path)
logger.info('section::', section_name)

# Start computation
with Client(cluster) as client:

    cluster.adapt(minimum = min_workers, maximum=max_workers)
    client.wait_for_workers(int(min_workers/2), 60*5)


    # Write Raw Images
    if not isdir(snakemake.output[0]):
        delayed_store = image.save_zarr(snakemake.params.raw_path, compute = False)
        logger.info('Writing Raw Images')
        future_store = client.persist(delayed_store)
        wait(future_store)
        logger.info('Finished Writing Raw Images')
        
    # Read from raw image zarr
    image = ia.get_HiSeqImages(image_path = snakemake.output[0])

    # Correct Background
    print('Correcting background')
    print('Pixel group adjustments')
#     for ch, values in image.config.items(image.machine+'background'):
#         print(f'Channel {ch}::',values)

    image.correct_background()
    image.register_channels()

    # Write Processed Images
    delayed_store = image.save_zarr(snakemake.params.save_path, compute = False)
    logger.info('Processing images')
    future_store = client.persist(delayed_store)
    wait(future_store)
    logger.info('Finished processing images')



# write section info to file
section_info = {'chunks_per_plane': ntiles,
                'planesize':image.im.nbytes,
                'path': snakemake.params.save_path,
                'machine': image.machine,
                'experiment': experiment_config['experiment']['experiment name']
               }
outputdir = Path(snakemake.params.save_path).parents[0]
with open(outputdir / f'{section_name}.yaml') as f:
    f.write(yaml.dump(section_info))
    
    

