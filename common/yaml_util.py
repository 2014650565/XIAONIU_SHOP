import yaml

def load_yaml(url:str):
    with open(url,'r',encoding='utf-8') as f:
        return yaml.safe_load(f)