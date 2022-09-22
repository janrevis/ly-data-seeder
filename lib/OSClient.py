

from ast import Dict
import json
import logging
from xmlrpc.client import Boolean
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

class OSClient:

  def __init__(self):
    self.host = 'search-local-yokelz-open-search-dev-ueeqriwmjsc52u5b475gqsoz7u.us-east-2.es.amazonaws.com'
    region = 'us-east-2'
    service = 'es'
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

    self.client = OpenSearch(
        hosts = [{'host': self.host, 'port': 443}],
        http_auth = awsauth,
        use_ssl = True,
        verify_certs = True,
        connection_class = RequestsHttpConnection
    )

  def has_index(self, index_name: str) -> Boolean:
    return self.client.indices.exists(index_name)

  def create_index(self, index_name: str, mapping: Dict) -> None:
    """
    Create an ES index.
    :param index_name: Name of the index.
    :param mapping: Mapping of the index
    """
    return self.client.indices.create(index=index_name, ignore=400, body=mapping)

  def add_doc(self, index_name, doc):
    return self.client.index(index=index_name, body=json.dumps(doc))

  def get_indices(self, index_name):
    return self.client.indices.get(index=index_name)

  def put_mapping(self, index_name, mapping):
    return self.client.indices.put_mapping(mapping, index=index_name)

  def delete_index(self, index_name):
    return self.client.indices.delete(index=index_name)