import os

import yaml


def load_yaml(url: str):
    if os.sep != '\\':
        url = url.replace('\\', os.sep)
    with open(url, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
