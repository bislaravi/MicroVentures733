from pyspark import SparkConf, SparkContext
from pyspark.sql.functions import udf
import uuid
from pyspark.sql import SQLContext, types, Row
from collections import OrderedDict
from pyspark.sql.types import *
from settings import CASSANDRA_SERVERS, \
    DATA_SET_INPUT_DIRECTORY, \
    CASSANDRA_KEY_SPACE, WORKERS
import json


class SparkBase(object):

    INPUT_DIRECTORY = DATA_SET_INPUT_DIRECTORY

    spark = None
    sql_ctx = None
    types = types

    def __init__(self, *args, **kwargs):
        self.conf = SparkConf().setAppName('Yelp Recommendation') \
            .set('spark.cassandra.connection.host', ','.join(CASSANDRA_SERVERS)) \
            .set('spark.dynamicAllocation.maxExecutors', 20)
        self.conf.setMaster('local[*]')
        try:
            self.spark = args[0]['spark_context']
            # self.spark.addPyFile('yelp_spark/cassandra_driver-3.12.0-py2.7-linux-x86_64.egg')
            # self.spark.addPyFile('yelp_spark/futures-3.1.1-py2.7.egg')
        except IndexError:
            self.spark = SparkContext(conf=self.conf)
            self.spark.setLogLevel("ERROR")
        self.sql_ctx = SQLContext(self.spark)

    def load_json_file(self, file):
        file_rdd = self.spark.textFile(file)
        return file_rdd.map(json.loads)

    def df_for(self, k_space, table):
        df = self.sql_ctx.read.format("org.apache.spark.sql.cassandra").\
            load(keyspace=k_space, table=table)
        df.createOrReplaceTempView(table)
        return df

    @staticmethod
    def convert_to_row(d: dict) -> Row:
        return Row(**OrderedDict(sorted(d.items())))

    @staticmethod
    def save_data_frame_to_cassandra(data_frame, table):

        data_frame.write \
            .format("org.apache.spark.sql.cassandra") \
            .mode('append') \
            .options(table=table, keyspace=CASSANDRA_KEY_SPACE) \
            .save()

spark_base = SparkBase()
