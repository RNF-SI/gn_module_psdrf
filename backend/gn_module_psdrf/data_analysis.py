import rpy2
import rpy2.robjects as robjects


def data_analysis(test):
    print('Do things in python here')
    # Now open a subprocess

    r = robjects.r

    r.source('/home/geonatureadmin/gn_module_psdrf/backend/gn_module_psdrf/Rscripts/generation_carnet.R')

    command = '../../../../../usr/bin/Rscript'
    arg = '--vanilla'
    path2script = '.\\psdrf_Analysis.r'
    

    # p = subprocess.Popen([command, path2script], stdout=subprocess.PIPE)
    # p.wait()
    # data = p.stdout.read()
    # print(data)
    
    return "test"