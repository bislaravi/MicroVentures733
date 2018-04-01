from yelp_spark import spark_base
from settings import DATA_SET_INPUT_DIRECTORY

from pyspark.sql.types import *

schema = StructType([
    StructField("by", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("time", TimestampType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("title", StringType(), True),
    StructField("type", StringType(), True),
    StructField("url", StringType(), True),
    StructField("text", StringType(), True),
    StructField("parent", StringType(), True),
    StructField("deleted", BooleanType(), True),
    StructField("dead", BooleanType(), True),
    StructField("descendants", IntegerType(), True),
    StructField("id", IntegerType(), True),
    StructField("ranking", IntegerType(), True)
])


df = spark_base.sql_ctx.read.load(DATA_SET_INPUT_DIRECTORY,
                                  format="csv",
                                  sep=",",
                                  schema=schema,
                                  header="true")











