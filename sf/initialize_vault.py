import hvac
import logging

## CONFIG

# Procedure if you don't know/have a root token/unseal key :
# 1. Don't panic
# 2. Kill the vault container
# 3. Launch clean-vault.sh
# 4. docker-compose up
# 5. Launch this script : a root_token and unseal_keys will be created

root_token = "e3cefd15-8c35-ae92-822b-26b1eb246cc2"
unseal_keys = ["8d01697f34881985b084db6f4562a2a12ee389bacbdf8df207a0dd76080ade3d"]

# Hard coded IPs are uncool. It should point to the vault basically.
url = "178.33.83.162:8200"
shares, threshold = 1, 1

#########

if __name__ == '__main__':
    client = hvac.Client(url=url)
    if not client.is_initialized():
        logging.warning("The vault is not initialized yet, it will be"
                        " initialized with {} keys and a threshold  of {}. Security is "
                        "overrated anyway.".format(shares, threshold))
        result = client.initialize(secret_shares=shares,
                                   secret_threshold=threshold)
        root_token, unseal_keys = result['root_token'], result['keys']
        logging.warning("Okay, initialized. The root_token is {} and the unseal"
                        " key(s) are {}. Keep that around, you'll "
                        "need it".format(root_token, unseal_keys))
    if client.is_sealed():
        logging.info('The vault is sealed. Unsealing...')
        client.unseal_multi(unseal_keys)
        logging.info('Everything is fine now')
    logging.info("Okay, you're good to go.")
