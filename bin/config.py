import yaml

with open("config.yaml") as f:
    conf = yaml.safe_load(f)

def old_get(var: str):
    for key, value in conf.items():
        if key == var:
            return value

# Not tested yet
def get(var: str):
    return conf[var]