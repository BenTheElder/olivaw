import os

from olivaw.compat import SafeConfigParser

global secrets
secrets = {}

def config_section_to_dict(config, section):
    section_dict = {}
    options = config.options(section)
    for option in options:
        section_dict[section+'.'+option] = config.get(section, option)
    return section_dict

def init(secrets_path=None):
    """initializes settings"""
    global secrets
    try:
        if secrets_path is None:
            secrets_path = os.environ["SECRETS_PATH"]
        config = SafeConfigParser()
        config.read(secrets_path)
        secrets = config_section_to_dict(config, 'telegram')
    except:
        # TODO
        pass
