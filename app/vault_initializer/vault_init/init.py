from typing import List

import hvac
import os
import logging
import requests

# Env config
import time

postgre_user = os.environ.get('POSTGRE_USER')
postgre_pwd = os.environ.get('POSTGRE_PWD')

# Config

postgre_db_host = 'app_db_1'
postgre_db_port = '5432'
postgre_database = 'postgres'
postgre_url = "postgresql://{}:{}@{}:{}/{}?sslmode=disable".format(postgre_user, postgre_pwd, postgre_db_host,
                                                                   postgre_db_port, postgre_database)

minitwit_host = 'app_minitwit_1'
minitwit_port = '5000'
minitwit_init_url = 'init'
minitwit_url = 'http://{}:{}/{}'.format(minitwit_host, minitwit_port, minitwit_init_url)

lease = '1h'
max_lease = '24h'

rw_role_request = """
CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';
    GRANT ALL ON ALL TABLES IN SCHEMA public TO \"{{name}}\";
"""

postgres_policy_name = 'postgres_read_policy'
postgres_policy = """
path "postgresql/creds/*" {
  policy = "write"
}
"""

# Hard coded IPs are uncool. It should point to the vault basically.
vault_host = "app_vault_1"
vault_port = 8200
vault_url = "http://{}:{}".format(vault_host, vault_port)

shares, threshold = 1, 1

consul_url = "http://178.33.83.163:8500"


#########

def init_postgre_backend(client: hvac.Client):
    if 'postgresql/' in client.list_secret_backends():
        logging.warning('Backend postgresql already exists : it will be modified')
    else:
        client.enable_secret_backend('postgresql')
    ok = False
    logging.info('Setting up the postgre backend with the url {}'.format(postgre_url))
    while not ok:
        try:
            # We try a lot because postgre/vault might not be completely up by the time it is launched
            client.write('/postgresql/config/connection', connection_url=postgre_url)
            ok = True
        except hvac.exceptions.InvalidRequest as e:
            logging.error(e)
            time.sleep(1)
#    logging.info('Setting lease to {} and max {}'.format(lease, max_lease))
#    client.write("postgresql/config/lease", lease=lease, max_lease=max_lease)
    logging.info('Creating role readwrite')
    client.write('/postgresql/roles/readwrite', sql=rw_role_request)
    logging.info("Ok we're good. You can now request rw on the url postgresql/creds/readwrite")


def pre_flight_check(client: hvac.Client) -> bool:
    if not client.is_initialized() or client.is_sealed():
        logging.error("The vault is either not initialized or sealed. That's odd.")
    elif not client.is_authenticated():
        logging.error("It seems the authentication token is invalid. Vault does"
                      " not like it. Clean everything up and come back.")
    else:
        logging.info("Everything looks good so far, pre-flight check ok")
        return True
    return False


def set_up_policies(client: hvac.Client):
    if postgres_policy_name in client.list_policies():
        logging.info("Policy {} already set up".format(postgres_policy_name))
        return
    client.set_policy(postgres_policy_name, postgres_policy)


def send_access_token(client: hvac.Client) -> bool:
    token = client.create_token(policies=[postgres_policy_name])
    requests.post(minitwit_url, json={'token': token['auth']['client_token']})


def reset_vault(client: hvac.Client) -> (str, List[str]):
    # Delete previous vault if it exists
    # requests.delete("{}/v1/kv/vault?recurse".format(consul_url))
    assert not client.is_initialized()
    logging.warning("The vault is not initialized yet, it will be initialized with {} keys and a threshold  of {}. "
                    "Security is overrated anyway.".format(shares, threshold))
    result = client.initialize(secret_shares=shares,
                               secret_threshold=threshold)
    root_token, unseal_keys = result['root_token'], result['keys']
    logging.warning("Okay, initialized. The root_token is {} and the unseal key(s) are {}. Keep that around, you'll"
                    " need it".format(root_token, unseal_keys))
    assert client.is_sealed()
    logging.info('The vault is sealed. Unsealing...')
    client.unseal_multi(unseal_keys)
    logging.info("Okay, you're good to go.")
    return root_token, unseal_keys


def main():
    client = hvac.Client(url=vault_url)
    root_token, _ = reset_vault(client)
    client.token = root_token
    if not pre_flight_check(client):
        exit(1)
    init_postgre_backend(client)
    set_up_policies(client)
    send_access_token(client)


if __name__ == '__main__':
    main()
