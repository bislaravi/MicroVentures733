import pickle
import sys
import json
import re
import codecs


class EntityParser(object):
    @staticmethod
    def LoadJsonEntity(filename):
        text = EntityParser.LoadStringEntityByFilename(filename)
        js = None
        try:
            if text:
                js = json.loads(text)
        except ValueError as e:
            print(e)
        return js

    @staticmethod
    def LoadStringEntityByFileHandler(fid):
        if fid:
            return pickle.load(fid)
        else:
            return ''

    @classmethod
    def LoadStringEntityByFilename(cls, filename, mode='rb'):
        fid = cls.get_file_handler(filename, mode)
        obj = None
        if fid:

            try:
                fid.seek(0)
                obj = pickle.load(fid)
            except ValueError as e:
                obj = None
        return obj

    @staticmethod
    def get_file_handler(filename, mode='r'):
        try:
            fid = open(filename, mode)
            fid.seek(0)
        except IOError:
            fid = None
        return fid


def main():
    path = sys.argv[0]
    js = EntityParser.LoadJsonEntity(path)

    if js:
        for i, item in enumerate(js):
            print("=============")
            for key in item.keys():
                print(key, "=", item[key])
    else:
        print("no json object")

if __name__ == "__main__":
    main()