import setuptools
from pathlib import Path


root_dir = Path(__file__).absolute().parent
with (root_dir / 'VERSION').open() as f:
    version = f.read()
with (root_dir / 'README.rst').open() as f:
    long_description = f.read()
with (root_dir / 'requirements.in').open() as f:
    requirements = f.read().splitlines()


setuptools.setup(
    name='gn_module_psdrf',
    version=version,
    description="Module GeoNature dédié au Protocole de Suivi Dendrométrique des Réserves Forestières",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    maintainer='Réserves Naturelles de France',
    url='https://github.com/RNF-SI/gn_module_psdrf',
    packages=setuptools.find_packages('backend'),
    package_dir={'': 'backend'},
    package_data={'gn_module_psdrf.migrations': ['data/*.sql']},
    install_requires=requirements,
    entry_points={
        'gn_module': [
            'code = gn_module_psdrf:MODULE_CODE',
            'picto = gn_module_psdrf:MODULE_PICTO',
            'blueprint = gn_module_psdrf.blueprint:blueprint',
            'migrations = gn_module_psdrf:migrations',
        ],
    },
    classifiers=['Development Status :: 1 - Planning',
                 'Intended Audience :: Developers',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3',
                 'License :: OSI Approved :: GNU Affero General Public License v3'
                 'Operating System :: OS Independent'],
)
