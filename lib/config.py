import os

import yaml
from mergedeep import merge

frontend_dir = os.path.join(os.path.dirname(os.path.abspath(os.path.dirname(__file__))), 'frontend')


def get_home_dir():
    home_dir = os.environ.get('HOME_DIR')
    if home_dir is None:
        home_dir = os.path.expanduser("~")
    return home_dir


def write_yaml(file, data):
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    with open(file, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


def read_yaml(file):
    if not os.path.exists(file):
        return {}
    with open(file, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def update_yaml(file, new_data):
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))
    data = read_yaml(file)
    merge(data, new_data)
    with open(file, "w") as outfile:
        yaml.dump(data, outfile, default_flow_style=False)


class Config:

    def __init__(self, **kwargs):
        # Set default directories
        self.config_path = os.path.join(get_home_dir(), '.tvh_iptv_config')
        self.config_file = os.path.join(self.config_path, 'settings.yml')

        self.settings = None

    def create_default_settings_yaml(self):
        self.settings = {
            "settings": {
                "tvheadend":                {},
                "default_ffmpeg_pipe_args": "-hide_banner -loglevel error "
                                            "-probesize 10M -analyzeduration 0 -fpsprobesize 0 "
                                            "-i [URL] -c copy -metadata service_name=[SERVICE_NAME] "
                                            "-f mpegts pipe:1",
                "refresh_schedule":         0000,

            }
        }
        self.write_settings_yaml(self.settings)

    def write_settings_yaml(self, data):
        write_yaml(self.config_file, data)

    def read_config_yaml(self):
        if not os.path.exists(self.config_file):
            self.create_default_settings_yaml()
        return read_yaml(self.config_file)

    def read_settings(self):
        if self.settings is None:
            self.settings = self.read_config_yaml()
        return self.settings

    def save_settings(self):
        if self.settings is None:
            self.create_default_settings_yaml()
        self.write_settings_yaml(self.settings)

    def update_settings(self, updated_settings):
        if self.settings is None:
            self.settings = self.read_config_yaml()
        merge(self.settings, updated_settings)


class FlaskConfig(object):
    basedir = os.path.abspath(os.path.dirname(__file__))
    config_path = os.path.join(get_home_dir(), '.tvh_iptv_config')
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    # Configure SQLite DB
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(config_path, 'db.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configure scheduler
    SCHEDULER_API_ENABLED = True

    # App configuration
    APP_CONFIG = Config()

    # Set up the App SECRET_KEY
    # SECRET_KEY = config('SECRET_KEY'  , default='S#perS3crEt_007')
    SECRET_KEY = os.getenv('SECRET_KEY', 'S#perS3crEt_007')

    # Assets Management
    ASSETS_ROOT = os.getenv('ASSETS_ROOT', os.path.join(frontend_dir, 'dist', 'spa'))


class FlaskProductionConfig(FlaskConfig):
    DEBUG = False


class FlaskDebugConfig(FlaskConfig):
    DEBUG = True


# Load all possible configurations
config_dict = {
    'Production': FlaskProductionConfig,
    'Debug':      FlaskDebugConfig
}
