import toml

file_default = "./"

def load_config(path=file_default + "config.toml"):
    # Loads the config from `path`
    
    cfg = toml.load(path)
    return cfg