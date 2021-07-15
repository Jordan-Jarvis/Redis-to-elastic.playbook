# Redis_Ingester
Builds a container that reads from a redis stream and pushes to elasticsearch.
## Environmental Variables
|Variable|Default|Description|
|--------|-------|-----------|
|redis_stream|mystream|Redis stream it reads from|
|sentinel_hosts|Redis servers with redis-sentinel it connects to|
|redis_port|6379|Port that is used for Redis|
|redis_batch_size|1|Max number of items per batch|
|redis_batch_timeout|1|Time in milliseconds between batches|
|elastic_host|Elasticsearch server that Redis pushes to|
## Testing

Requirements
- docker
- docker-compose
- redis-tools
- aioify
- elasticsearch
- redis
- aioredis
- asyncio
- pydantic
- aredis

Build and start the docker environment

    docker-compose build
    docker-compose up

## Functional test
Start the docker-compose environment (see previous section)

    pipenv install
    pipenv run pytest

## Vagrant Test
Install Vagrant plugin and bring up the environment by running:

    vagrant plugin install vagrant-docker-compose
    vagrant up

## Concourse testing
Whenever a git push is done on the gitops branch of this repo it will update the concourse pipeline automatically. You can check _____ to ensure it is passing the tests
