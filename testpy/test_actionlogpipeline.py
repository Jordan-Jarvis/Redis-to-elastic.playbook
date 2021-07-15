"""This file tests that redis, logstash and elasticsearch all work"""

import pytest
import asyncio
import redis as _redis
import elasticsearch as _elasticsearch
import time
import multiprocessing as mp
import subprocess
from pylogstash.receivers import RedisReceiver
from pylogstash.dispatchers import ElasticDispatcher
from pylogstash.config import settings
import sys
import os

@pytest.fixture
def receiver():
    manager = mp.Manager()
    shared_list = manager.dict(        {
            'indexes' : {},
            'requests' : 0,
        })
    r = RedisReceiver(sentinel_hosts=settings.sentinel_hosts, port=settings.redis_port, db=0, batch_size=settings.redis_batch_size, timeout=settings.redis_batch_timeout, shared_list = shared_list)
    return r

@pytest.fixture
def dispatcher():
    d = ElasticDispatcher(host=settings.elastic_host)
    return d
    


@pytest.fixture
def connect_systems():
    r = RedisReceiver(host=settings.redis_host, port=settings.redis_port, db=0, batch_size=settings.redis_batch_size, timeout=settings.redis_batch_timeout)
    r.subscribe(settings.redis_stream)
    d = ElasticDispatcher(host=settings.elastic_host, port=settings.elastic_port, index=settings.elastic_index)
    d.connect(r)
    return d




def test_redis_subscribe(receiver):
    streamslist = ['mystream','yourstream']
    streamsSet = set(streamslist)
    streamsTuple = tuple(streamslist)
    datatypes = [streamslist,streamsSet, streamsTuple]
    for datatype in datatypes:
        receiver.subscribe(datatype)
        assert 'mystream' in receiver.streams
        assert 'yourstream' in receiver.streams



    
    #dispatcher.streams = {'mystream': '0-0', 'yourstream': '0-0'}
    #assert dispatcher.streams == {'mystream': '0-0', 'yourstream': '0-0'}
    #assert dispatcher.r.last_index == dispatcher.last_index


def test_elastic_disconnect(receiver, dispatcher):
    dispatcher.connect(receiver) 
    assert dispatcher.r == receiver
    dispatcher.disconnect()
    assert dispatcher.r == None

def test_convert_to_utf8(dispatcher):
    tmp = dispatcher.convert_to_utf8({b'hello':{b'testme':{b'convertme':'testme'}}})
    assert tmp == {'hello':{'testme':{'convertme':'testme'}}}

    
def test_get_last_indexes(receiver, dispatcher):
    receiver.subscribe((settings.redis_stream,"yourstream"))
    dispatcher.connect(receiver)
    tmp = receiver.get_last_indexes()
    assert None != tmp['mystream']
    assert None != tmp['yourstream']

def test_set_last_indexes(receiver):
    last_indexes = {'mystream': '1618349003513-0', 'yourstream': '1618414435898-6'}
    receiver.set_last_indexes(last_indexes)
    assert last_indexes == receiver.shared_list['indexes']

def test_subscribe(receiver):
    streams = ['yourstream', 'mystream']
    streamst = tuple(streams)
    streamsset = set(streams)
    receiver.subscribe(streams)
    assert receiver.streams == streams
    receiver.subscribe(streamst)
    assert receiver.streams == streams
    receiver.subscribe(streamsset)
    assert receiver.streams == streams or ['mystream', 'yourstream']
    receiver.subscribe('yourstream')
    assert receiver.streams == ['yourstream']

def test_convert_datatypes(receiver):
    streams = {'mystream': '1618349003513-0', 'yourstream': '1618414435898-6'}

def test_set_formatted_stream_index(receiver, dispatcher):
    dispatcher.connect(receiver)
    last_indexes = {'mystream': '1618349003513-0', 'yourstream': '1618414435898-6'}
    dispatcher.r.shared_list['indexes'] = last_indexes
    dispatcher.set_formatted_stream_index()
    assert dispatcher.r.formatted_stream_index == ['mystream','yourstream','1618349003513-0','1618414435898-6']


def test_end_to_end(dispatcher, receiver):
    
    ls_output=subprocess.Popen(["python3.8","./pylogstash/main.py"])
    time.sleep(2)
    dispatcher.connect(receiver)
    os.system(f"redis-cli -h {receiver.host} < ./pylogstash/redis_test.txt")
    time.sleep(2)
    result = dispatcher.es.search(body={"query": {"query_string": {"query":"iamatest"}}})
    print(result)
    print(result["hits"]["hits"][0]["_id"], "This should be the id")
    dispatcher.es.delete(index=settings.redis_stream,doc_type="_doc",id=result["hits"]["hits"][0]["_id"])

     
