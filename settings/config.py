DATA_SET_INPUT_DIRECTORY = 'data/hacker_news_full/'
WORKERS = ''

import os


def path_to_data_file(path):
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(cur_dir, path))

data = '../data/data.csv'
train = '../data/train_data.csv'
test = '../data/train_data.csv'


MYSQL_HOST='vcap.cj1yc0lsubr8.us-west-1.rds.amazonaws.com'
MYSQL_PORT='3306'
MYSQL_DATABASE='crunchbase'
MYSQL_USER='microventure'
MYSQL_PASSWORD='immadvcap733'

DATA_FILE = path_to_data_file(data)
TRAIN_FILE = path_to_data_file(train)
TEST_FILE = path_to_data_file(test)