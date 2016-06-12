# Minitwit application

## Component

* Minitwit : the actual application, serving as a front end
* Postgres : the db in which minitwit stores everything
* Vault : The vault used by minitwit to get credentials to connect to postgres
* Vault_init : A little script to set everything up

## Vault_init :

It will initialize the vault, unseal it, put the required config for the
postgres backend and provides an access token to minitwit

## Vault :

KV store for secrets, will provide credentials for postgre access. Inmem, not consul.

## Postgres :

Nothing specific, just a db. Access is controled by vault

## Minitwit:

Appli, accessible on 0.0.0.0:5000. A label must be set on the dockercompose to know where it lands (optionnal though,
docker ps does the job)

# Launch :

That's it !

```
docker-compose up --build
```
