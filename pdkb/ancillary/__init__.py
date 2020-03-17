
import glob, os

py_files = glob.glob('/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/*.py')
py_files = [x for x in py_files if '__init__' not in x]

def compute_modules():
    return ['pdkb.ancillary.' + mod for mod in [x.split('/')[-1].split('.')[0] for x in py_files]]
