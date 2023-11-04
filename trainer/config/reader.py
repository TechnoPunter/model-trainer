import os

import yaml


def read_config(file_path: str = 'resources/config/config.yaml'):
    with open(file_path, 'r') as file:
        parent_config = yaml.safe_load(file)

    file_directory = os.path.dirname(file_path)

    # Get the list of included YAML filenames from the parent config
    child_file_paths = parent_config.get('include', [])

    merged_config = {}
    for child_file_path in child_file_paths:
        try:
            with open(file_directory + "/" + child_file_path + "-local.yaml", 'r') as child_file:
                child_config = yaml.safe_load(child_file)
        except FileNotFoundError:
            with open(file_directory + "/" + child_file_path + ".yaml", 'r') as child_file:
                child_config = yaml.safe_load(child_file)

        # Merge the child_config into the merged_config using update()
        merged_config.update(child_config)

    parent_config.pop('include', [])
    parent_config.update(merged_config)

    return parent_config


try:
    cfg = read_config()
    cfg['generated'] = "generated/"
except FileNotFoundError:
    cfg = read_config('../../resources/config/config.yaml')
    cfg['generated'] = '../../generated/'

# Example usage:
if __name__ == '__main__':
    config = read_config('../../resources/config/config.yaml')
    print(yaml.dump(config))
