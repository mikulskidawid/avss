import configparser, tempfile, os

# creates or modifies tmp file
def saveTMP(data_dict, temp_config_file_path=None):
    tempfile.tempdir = "data/tmp"
    config = configparser.ConfigParser()

    if temp_config_file_path is not None and os.path.exists(temp_config_file_path):
        config.read(temp_config_file_path)

    if 'DATA' not in config:
        config['DATA'] = {}

    for key, value in data_dict.items():
        config['DATA'][key] = str(value)

    if temp_config_file_path is None:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.tmp') as temp_config_file:
            temp_config_file_path = temp_config_file.name

    with open(temp_config_file_path, 'w') as file:
        config.write(file)

    return temp_config_file_path

# reads tmp file
def loadTMP(temp_config_file_path):
    config = configparser.ConfigParser()
    config.read(temp_config_file_path)

    data_dict = {}
    if 'DATA' in config:
        data_dict = dict(config['DATA'])

    return data_dict

# prepares new tmp file with default values
def createTMP():
    data = {
        'restart_stream': False, 
        'restart_www': False, 
        'close_system': False, 
        'reset_system': False
        }
    return saveTMP(data)