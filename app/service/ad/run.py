#Este modulo se encarga de solicitar
#el cambio de credenciales de los users
#podría sustituirse por un script de
#powershell

import os
import json
from ldap3 import Server, Connection, ALL, NTLM, ALL_ATTRIBUTES, ALL_OPERATIONAL_ATTRIBUTES, AUTO_BIND_NO_TLS, SUBTREE, MODIFY_REPLACE
from ldap3.core.exceptions import LDAPCursorError


def ad(users, config=None):
    if config is None:
        print("[AD] No configuration provided")
        return []
    
    data = config.getAdConfig()
    ad_user = data['user']
    ad_pass = data['pass']
    server = data['server']
    domain = data['domain']
    skip = data['skip']

    try:
        targets = []
        for user in users:
            if user not in skip:
                targets.append(user)
        server = Server(server, get_info=ALL)
        conn = Connection(server, user="{}\\{}".format(domain, ad_user), password=ad_pass, authentication=NTLM, auto_bind=True)
        for user in targets:
            conn.search(search_base='DC={},DC=com'.format(domain), search_filter='(&(objectClass=user)(sAMAccountName={}))'.format(user), search_scope=SUBTREE, attributes=ALL_ATTRIBUTES, get_operational_attributes=True)
            if len(conn.entries) == 0:
                config.log.warn("[AD] User {} not found".format(user))
                continue
            entry = conn.entries[0]
            #Change pwdLastSet to 0
            conn.modify(entry.entry_dn, {'pwdLastSet': [(MODIFY_REPLACE, ['0'])]})
            config.log.info("[AD] User {} reset".format(user))
            #Commit changes
            
        conn.unbind()
        return targets

    except Exception as e:
        config.log.error("[AD] Error: {}".format(e))
        return []