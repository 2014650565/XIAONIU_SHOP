import csv

def csv_load(url:str):
    with open(url,'r',encoding='utf-8') as f:
        return list(csv.reader(f))[1:]