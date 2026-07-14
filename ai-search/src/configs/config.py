from pathlib import Path
import yaml


class Config:
    """
    Loads project configuration.
    """

    def __init__(self, path: str = "src/configs/default.yaml"):
        self.path = Path(path)

        with open(self.path, "r") as f:
            self.config = yaml.safe_load(f)

    def __getitem__(self, key):
        return self.config[key]

    def get(self, *keys):
        value = self.config
        for key in keys:
            value = value[key]
        return value