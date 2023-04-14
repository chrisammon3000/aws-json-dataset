import sys
sys.path.append("../awsjsondataset")
import json
import pytest
from awsjsondataset.exceptions import InvalidJsonDataset
from awsjsondataset.utils import (
    get_record_size_kb,
    sort_records_by_size_kb,
    validate_data,
    queue_records,
    queue_records_batch,
    publish_record,
    publish_records_batch,
    put_record,
    put_records_batch
)
from tests.fixtures import *

def test_get_record_size_kb():
    record = {"a": 1}
    assert get_record_size_kb(record) == 0.06

def test_sort_records_by_size_kb():
    records = [{"a": 1}, {"b": 1234567891011}]
    assert sort_records_by_size_kb(records) == [(records[0], 0.06), (records[1], 0.07)]

    records = [{"a": 1}, {"b": 1234567891011}]
    assert sort_records_by_size_kb(records, ascending=False) == [(records[1], 0.07), (records[0], 0.06)]

def test_validate_data():
    data = [{"a": 1}, {"b": 1234567891011}]
    assert validate_data(data) == data

    data = [1, 2, 3]
    with pytest.raises(InvalidJsonDataset):
        validate_data(data)

### SQS ###
@mock_sqs
def test_queue_records(sqs):

    # create a mock resource
    QUEUE_URL = 'queue-url'
    sqs.create_queue(QueueName=QUEUE_URL)

    data = [{"a": 1}, {"b": 2}]
    assert queue_records(sqs, data, QUEUE_URL) == None

@mock_sqs
def test_queue_records_batch(sqs):
    
    # create a mock resource
    QUEUE_URL = 'queue-url'
    sqs.create_queue(QueueName=QUEUE_URL)

    # test for 3 batches
    data = [ {idx:idx+1} for idx in range(30) ]
    assert queue_records_batch(sqs, data, QUEUE_URL) == None

    # test for total in batch over 256kb
    data = [ {"field": "value"*10000} for idx in range(30) ]
    assert queue_records_batch(sqs, data, QUEUE_URL) == None

    # test for records over 256kb
    data = [ {"field": "value"*100000} for idx in range(30) ]
    with pytest.raises(Exception):
        queue_records_batch(sqs, data, QUEUE_URL)

    # test for 1 batch less than 10 records
    data = [ {idx:idx+1} for idx in range(5) ]
    with pytest.raises(Exception):
        queue_records_batch(sqs, data, QUEUE_URL)

### SNS ###
@mock_sns
def test_publish_record(sns):
    
    # create a mock resource
    response = sns.create_topic(Name="test-topic")
    TOPIC_ARN = response['TopicArn']

    data = {"a": 1}
    response = publish_record(sns, data, TOPIC_ARN)
    assert response['ResponseMetadata']['HTTPStatusCode'] == 200


@mock_sns
def test_publish_records_batch(sns):
        
    # create a mock resource
    response = sns.create_topic(Name="test-topic")
    TOPIC_ARN = response['TopicArn']

    # test for 3 batches
    data = [ {idx:idx+1} for idx in range(30) ]
    response = publish_records_batch(client=sns, messages=data, topic_arn=TOPIC_ARN)
    assert response is None

    # test for total in batch over 256kb
    data = [ {"field": "value"*10000} for idx in range(30) ]
    response = publish_records_batch(client=sns, messages=data, topic_arn=TOPIC_ARN)
    assert response is None

    # test for error with records over 256kb
    data = [ {"field": "value"*100000} for idx in range(30) ]
    with pytest.raises(Exception):
        publish_records_batch(client=sns, messages=data, topic_arn=TOPIC_ARN)

    # test for error with 1 batch less than 10 records
    data = [ {idx:idx+1} for idx in range(5) ]
    with pytest.raises(Exception):
        publish_records_batch(client=sns, messages=data, topic_arn=TOPIC_ARN)
        
### Kinesis ###
@mock_firehose
def test_put_record(s3, firehose):

    # create a mock bucket
    DATA_BUCKET_NAME = 'data-bucket'
    response = s3.create_bucket(Bucket=DATA_BUCKET_NAME)

        # create a mock delivery stream
    DELIVERY_STREAM_NAME = "data-delivery-stream"
    response = firehose.create_delivery_stream(
        DeliveryStreamName=DELIVERY_STREAM_NAME,
        ExtendedS3DestinationConfiguration={
            'RoleARN': 'arn:aws:iam::123456789012:role/firehose_delivery_role',
            'BucketARN': f'arn:aws:s3:::{DATA_BUCKET_NAME}'
        })

    response = put_record(
        client=firehose,
        stream_name=DELIVERY_STREAM_NAME,
        data='{"test_field":"test_key"}')
    assert "RecordId" in response

    with pytest.raises(Exception):
        put_record(
            client=firehose,
            stream_name=DELIVERY_STREAM_NAME,
            data={"test_field":"test_key"*1000000}
        )

@mock_firehose
def test_put_records_batch(s3, firehose):
    
    # create a mock bucket
    DATA_BUCKET_NAME = 'data-bucket'
    response = s3.create_bucket(Bucket=DATA_BUCKET_NAME)

    # create a mock delivery stream
    DELIVERY_STREAM_NAME = "data-delivery-stream"
    response = firehose.create_delivery_stream(
        DeliveryStreamName=DELIVERY_STREAM_NAME,
        ExtendedS3DestinationConfiguration={
            'RoleARN': 'arn:aws:iam::123456789012:role/firehose_delivery_role',
            'BucketARN': f'arn:aws:s3:::{DATA_BUCKET_NAME}'
        })

    # test for ideal case
    data = [ {idx:idx+1} for idx in range(499) ]
    response = put_records_batch(
        client=firehose,
        stream_name=DELIVERY_STREAM_NAME,
        records=data)
    assert response is None

    # test for large batch
    data = [ {idx:idx+1} for idx in range(3000) ]
    response = put_records_batch(
        client=firehose,
        stream_name=DELIVERY_STREAM_NAME,
        records=data)
    assert response is None

    # test for small batch
    data = [ {idx:idx+1} for idx in range(10) ]
    response = put_records_batch(
        client=firehose,
        stream_name=DELIVERY_STREAM_NAME,
        records=data)
    assert response is None

    # test for error with too small batch
    with pytest.raises(Exception):
        data = [ {idx:idx+1} for idx in range(9) ]
        response = put_records_batch(
            client=firehose,
            stream_name=DELIVERY_STREAM_NAME,
            records=data)

    # test for total in batch over 256kb
    data = [ {"field": "value"*10000} for idx in range(30) ]
    response = put_records_batch(
        client=firehose,
        stream_name=DELIVERY_STREAM_NAME,
        records=data)
    assert response is None

    # test for error with records over 256kb
    data = [ {"field": "value"*1000000} for idx in range(30) ]
    with pytest.raises(Exception):
        put_records_batch(
            client=firehose,
            stream_name=DELIVERY_STREAM_NAME,
            records=data)
    
    del data