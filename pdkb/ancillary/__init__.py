
import glob, os

py_files = glob.glob('/'.join(os.path.realpath(__file__).split('/')[:-1]) + '/*.py')
py_files = filter(lambda x: '__init__' not in x, py_files)

def compute_modules():
    return ['pdkb.ancillary.' + mod for mod in map(lambda x: x.split('/')[-1].split('.')[0], py_files)]
