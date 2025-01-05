import os
import importlib

def get_config():

    env = os.getenv('FLASK_ENV', 'local')

    # Dynamically import the settings module based on the environment
    try:
        config_module = importlib.import_module(f'settings.{env}')
        return config_module.Config
    except ModuleNotFoundError:
        raise ImportError(f"Settings module for environment '{env}' not found!")
