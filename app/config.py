import os
import sys
import json
import logging
import tempfile
import jsonschema
from jsonschema import validate

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class AutocrackerLogger(logging.getLoggerClass()):
    def __init__(self, name, level=logging.NOTSET):
        super(AutocrackerLogger, self).__init__(name, level)
        self.setLevel(level)
        self.buffer = []

    def __call__(self, *args, **kwargs):
        return self

    #Debug level
    def debug(self, msg, *args, **kwargs):
        self.buffer.append(msg)
        super(AutocrackerLogger, self).debug(msg, *args, **kwargs)

    #Info level
    def info(self, msg, *args, **kwargs):
        self.buffer.append(msg)
        super(AutocrackerLogger, self).info(msg, *args, **kwargs)
    
    #Warning level
    def warn(self, msg, *args, **kwargs):
        self.buffer.append(msg)
        super(AutocrackerLogger, self).warn(msg, *args, **kwargs)

    #Error level
    def error(self, msg, *args, **kwargs):
        self.buffer.append(msg)
        super(AutocrackerLogger, self).error(msg, *args, **kwargs)

    #Critical level
    def critical(self, msg, *args, **kwargs):
        self.buffer.append(msg)
        super(AutocrackerLogger, self).critical(msg, *args, **kwargs)

    def getLogBuffer(self):
        return self.buffer

class ConfigBase:
    PERFORM_VALIDATION = os.environ.get('PERFORM_VALIDATION', 'True')

    SCHEMA_FOLDER = os.getcwd() + "/" + os.environ.get('SCHEMA_FOLDER', 'schemas/')
    CONF_FOLDER = os.getcwd() + "/" + os.environ.get('CONF_FOLDER', 'conf/')

    AD_CONF = os.environ.get('AD_CREDS', CONF_FOLDER + 'creds/ad.json')
    EMAIL_CONF = os.environ.get('EMAIL_CREDS', CONF_FOLDER + 'creds/email.json')
    PENTERA_CONF = os.environ.get('PENTERA_CREDS', CONF_FOLDER + 'creds/pentera.json')
    GENERIC_CONF = os.environ.get('GENERIC_CREDS', CONF_FOLDER + 'conf.json')

    AD_SCHEMA = os.environ.get('AD_SCHEMA', SCHEMA_FOLDER + 'creds/ad.json')
    EMAIL_SCHEMA = os.environ.get('EMAIL_SCHEMA', SCHEMA_FOLDER + 'creds/email.json')
    PENTERA_SCHEMA = os.environ.get('PENTERA_SCHEMA', SCHEMA_FOLDER + 'creds/pentera.json')
    GENERIC_SCHEMA = os.environ.get('GENERIC_SCHEMA', SCHEMA_FOLDER + 'conf.json')

    def __init__(self):
        print("Dir: {}".format(os.getcwd()))
        self.valid = False
        self.perform_validation = self.PERFORM_VALIDATION == 'True'
        try:
            self.generic_schema = self.__load(self.GENERIC_SCHEMA)
            self.ad_schema = self.__load(self.AD_SCHEMA)
            self.email_schema = self.__load(self.EMAIL_SCHEMA)
            self.pentera_schema = self.__load(self.PENTERA_SCHEMA)

        except Exception as e:
            print("[CONFIG] Error loading schemas, validation is disabled: {}".format(e))
            self.perform_validation = False
        try:
            self.data = self.__load(self.GENERIC_CONF)
            self.ad = self.__load(self.AD_CONF)
            self.email = self.__load(self.EMAIL_CONF)
            self.pentera = self.__load(self.PENTERA_CONF)
            
            if self.perform_validation:
                print("[CONFIG] Validating configuration...")
                validate(instance=self.data, schema=self.generic_schema)
                validate(instance=self.ad, schema=self.ad_schema)
                validate(instance=self.email, schema=self.email_schema)
                validate(instance=self.pentera, schema=self.pentera_schema)

            if os.path.isfile(self.data["logfile"]):
                logging.basicConfig(
                    level=logging.INFO,
                    filename=self.data["logfile"],
                    filemode="a+",
                    format="%(asctime)-15s %(levelname)-8s %(message)s"
                )
            else:
                logging.basicConfig(
                    level=logging.INFO,
                    stream=sys.stdout,
                    filemode="a+",
                    format="%(asctime)-15s %(levelname)-8s %(message)s"
                )
                logging.warn("[CONFIG] Logging file doesnt exist, outputting to stdout instead")
            self.log = AutocrackerLogger('root')
            self.log.info("[CONFIG] Login started")
            self.valid = True

        except jsonschema.exceptions.ValidationError as e:
             self.log.error("[CONFIG] Error validating configuration: {}".format(e))

        except Exception as e:
            self.log.error("[CONFIG] Error loading configuration: {}".format(e))

    def __load(self, file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise Exception("[CONFIG] Error loading configuration file: {}, exception: {}".format(file, e))

    def getGenericConfig(self):
        return self.data

    def getAdConfig(self):
        return self.ad

    def getEmailConfig(self):
        return self.email

    def getPenteraConfig(self):
        return self.pentera

    def isValid(self):
        return self.valid

class Config(ConfigBase, metaclass=Singleton):
    pass