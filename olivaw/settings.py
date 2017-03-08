from olivaw.compat import SafeConfigParser

global secrets
secrets = {}

def config_section_to_dict(config, section):
    section_dict = {}
    options = config.options(section)
    for option in options:
        section_dict[section+'.'+option] = config.get(section, option)
    return section_dict

config = SafeConfigParser()
config.read("secrets.cfg")
secrets = config_section_to_dict(config, 'telegram')
