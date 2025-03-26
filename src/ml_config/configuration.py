from abc import abstractmethod
from dataclasses import dataclass, field, fields
from typing import ClassVar

import yaml


@dataclass
class BaseConfig:
    subconfigs: ClassVar[dict] = {}

    @classmethod
    @abstractmethod
    def init_subconfig(cls, subconfig_name, subconfig_dict):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, kwargs: dict):
        valid_keys = {f.name for f in fields(cls)}
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_keys}
        filtered_kwargs = {}
        for k, v in kwargs.items():
            if k not in valid_keys:
                continue
            if k in cls.subconfigs.keys():
                if isinstance(v, dict):
                    filtered_kwargs[k] = cls.init_subconfig(k, v)
                elif isinstance(v, cls.subconfigs[k]):
                    filtered_kwargs[k] = v
                else:
                    raise ValueError(f"Invalid type for {k}")
            else:
                filtered_kwargs[k] = v

        return cls(**filtered_kwargs)

    def to_dict(self):
        out_dict = {}
        for key, item in self.__dict__.items():
            if key in self.subconfigs and isinstance(item, BaseConfig):
                out_dict[key] = item.to_dict()
            else:
                out_dict[key] = item
        return out_dict

    @classmethod
    def inherit(cls, parent, **kwargs):
        parent_dict = parent.to_dict()
        parent_dict.update(kwargs)
        return cls.from_dict(parent_dict)

    @classmethod
    def from_yaml(cls, path: str):
        with open(path) as f:
            _obj = cls.from_dict(yaml.safe_load(f))
            _obj.load_path = path

        return _obj

    def to_yaml(self, path):
        with open(path, "w") as f:
            yaml.safe_dump(self.to_dict(), f)


@dataclass
class ExampleDataConfig(BaseConfig):
    root: str

@dataclass
class ExampleExperimentConfig(BaseConfig):
    exp_id: str
    data: ExampleDataConfig

    subconfigs: ClassVar[dict] = {
        "data": ExampleDataConfig,
    }

    @classmethod
    def init_subconfig(cls, subconfig_name, subconfig_dict) -> BaseConfig | dict:
        if subconfig_name not in cls.subconfigs:
            return subconfig_dict
        if subconfig_name == "data":
            return ExampleDataConfig.from_dict(subconfig_dict)


def save_config(exp_config: ExampleExperimentConfig, time_id: str) -> None:
    "save config to yaml"
    import os

    os.makedirs("results/configs", exist_ok=True)
    exp_config.to_yaml(f"results/configs/exp_config_{time_id}.yaml")
