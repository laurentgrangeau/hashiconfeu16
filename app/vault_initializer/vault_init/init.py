import hvac
import os
import logging
import requests

# Env config

access_token = os.environ.get('VAULT_TOKEN')
postgre_user = os.environ.get('POSTGRE_USER')
postgre_pwd = os.environ.get('POSTGRE_PWD')

# Config

postgre_db_host = 'app_db_1'
postgre_db_port = '5432'
postgre_database = 'postgres'

minitwit_host = 'app_minitwit_1'
minitwit_port = '5000'
minitwit_init_url = 'init'

lease = '1h'
max_lease = '24h'

rw_role_request = """
CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}';
    GRANT ALL ON ALL TABLES IN SCHEMA public TO \"{{name}}\";
"""

postgres_read_policy_name = 'postgres_read_policy'
postgres_read_policy = """
path "postgresql" {
  policy = "read"
}
"""

# Hard coded IPs are uncool. It should point to the vault basically.
url = "178.33.83.162:8200"


#########

def init_postgre_backend(client: hvac.Client):
    client.enable_secret_backend('postgresql')
    connection_url = "postgresql://{}:{}@{}:{}/{}".format(postgre_user, postgre_pwd, postgre_db_host, postgre_db_port,
                                                          postgre_database)
    logging.info('Creating the postgre backend with the url {}'.format(connection_url))
    client.write("postgresql/config/connection", connection_url=connection_url)
    logging.info('Setting lease to {} and max {}'.format(lease, max_lease))
    client.write("postgresql/config/lease", lease=lease, max_lease=max_lease)
    logging.info('Creating role rw')
    client.write("postgresql/roles/rw", sql=rw_role_request)
    logging.info("Ok we're good. You can now request rw on the url postgresql/creds/rw")


def pre_flight_check(client: hvac.Client) -> bool:
    if not access_token:
        logging.error("No token is provided. Make sure you give a root token"
                      "via the env var VAULT_TOKEN.")
    elif not client.is_initialized() or client.is_sealed():
        logging.error("The vault is either not initialized or sealed. Please "
                      "take care of that (script initialize_vault.py in the sf")
    elif not client.is_authenticated():
        logging.error("It seems the authentication token is invalid. Vault does"
                      " not like it. Clean everything up and come back.")
    else:
        logging.info("Everything looks good so far, pre-flight check ok")
        return True
    return False


def set_up_policies(client: hvac.Client):
    if postgres_read_policy_name in client.list_policies():
        logging.info("Policy {} already set up".format(postgres_read_policy_name))
        return
    client.set_policy(postgres_read_policy_name, postgres_read_policy)


def send_access_token(client: hvac.Client) -> bool:
    minitwit_url = '{}:{}/{}'.format(minitwit_host, minitwit_port, minitwit_init_url)
    token = client.create_token(policies=[postgres_read_policy_name])
    requests.post(minitwit_url, json={'token': token})


## Might be cool to add a bootstrapper : create a role that can grand permissions, and use that role instead.

def main():
    client = hvac.Client(url=url)
    client.token = access_token
    if not pre_flight_check(client):
        exit(1)
    init_postgre_backend(client)
    set_up_policies(client)


if __name__ == '__main__':
    main()
