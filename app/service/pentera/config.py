#Este modulo se encarga de leer
#y exponer toda la configuracion

import os
import json
#Configuracion de la api de pentera

class config:
    DATAFILE = os.environ.get('PENTERA_CREDS', 'conf/creds/pentera.json')
    data = None

    @staticmethod
    def get(key):
        if config.data is None:
            config.data = config._load()
        return config.data.get(key, None)

    def _load():
        with open(config.DATAFILE, 'r') as f:
            return json.load(f)

    def _save():
        with open(config.DATAFILE, 'w') as f:
            json.dump(config.data, f, indent=4)

    def set(key, value):
        if config.data is None:
            config.data = config._load()
        config.data[key] = value
        config._save()

    def __init__(self):
        pass