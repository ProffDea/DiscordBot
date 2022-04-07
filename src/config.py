import yaml

with open("config.yaml") as f:
    conf = yaml.safe_load(f)


def get(var: str):
    return conf[var]


def refresh():
    pass
