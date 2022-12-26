#Este es el modulo principal
#Solo sirve para llamar en orden a los
#servicios, escribir el last_run y 
#emitir logs a disco.
import os
import sys
import logging
import app.service.pentera.run
import app.service.ad.run
import app.service.email.run

from app.config import Config 

def main():
    print("[MAIN] Loading configuration...")
    conf = Config()
    if not conf.isValid():
        print("[MAIN] Configuration is invalid, exiting...")
        return

    conf.log.info("[MAIN] Login starting...")
    conf.log.info("[MAIN] Cracking passwords...")
    
    cracked = app.service.pentera.run.pentera(conf=conf)
    if len(cracked) == 0:
        logging.warning("[MAIN] No passwords were cracked")
        return

    logging.info("[MAIN] Cracked users: {}".format(cracked))
    conf.log.info("[MAIN] Resetting passwords...") 

    resets = app.service.ad.run.ad(cracked, config=conf)
    if len(resets) == 0:
        conf.log.error("[MAIN] No users were reset")
        return

    conf.log.info("[MAIN] Sending emails...")
    app.service.email.run.email(resets, config=conf)
    conf.log.info("[MAIN] Emails sent, exiting main thread!")