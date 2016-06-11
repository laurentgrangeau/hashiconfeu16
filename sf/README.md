# Software factory

## Components

* Gitlab
* Artifactory
* Vault
* Jenkins

## Vault

The vault is launched in dev mode, pointing to the consul cluster on which the
swarm is put.

It might be necessary to clean the space in consul before it can be set up, see 
the script clean-vault.sh to do that 

After the first launch, you will get an unseal key and a root token in the logs
of the container, keep them !

	Unseal Key: 8d01697f34881985b084db6f4562a2a12ee389bacbdf8df207a0dd76080ade3d
	Root Token: e3cefd15-8c35-ae92-822b-26b1eb246cc2

You can unseal with the python client.

Just check *initialize_vault.py* to see how it works.
