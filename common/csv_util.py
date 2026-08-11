import csv
import os


def csv_load(url: str):
    if os.sep != '\\':
        url = url.replace('\\', os.sep)
    with open(url,'r',encoding='utf-8') as f:
        return list(csv.reader(f))[1:]
