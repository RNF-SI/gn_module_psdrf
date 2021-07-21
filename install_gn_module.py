import os
import subprocess
import psycopg2
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent



def gnmodule_install_app(gn_db, gn_app):
    '''
        Fonction principale permettant de réaliser les opérations d'installation du module : 
            - Base de données
            - Module (pour le moment rien)
    '''
    with gn_app.app_context() :
        table_sql = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/psdrf.sql')
        data_sql = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/psdrf_data.sql')
        
        gn_db.session.execute(open(table_sql, 'r').read())
        gn_db.session.commit()
        gn_db.session.execute(open(data_sql, 'r').read())
        gn_db.session.commit()

