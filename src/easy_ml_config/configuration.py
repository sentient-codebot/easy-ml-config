import types
from dataclasses import dataclass, fields, MISSING
from typing import ClassVar, get_type_hints, get_origin, get_args, Union

import yaml


@dataclass
class BaseConfig:
    """
    BaseConfig is a base class you can inherit from to get access to a series of \
        convient utility methods.

    Methods:
        from_dict(kwargs: dict): 
            Create a configuration instance from a dictionary.
            
        to_dict(): 
            Convert the configuration object to a dictionary.
            
        from_yaml(path: str): 
            Create a configuration instance from a YAML file.
            
        to_yaml(path: str): 
            Save the configuration object to a YAML file.
            
        inherit(parent, **kwargs): 
            Create a new configuration instance by inheriting from a parent 
            configuration with optional overrides.

    Example usage:
        ```python
        from dataclasses import dataclass
        from easy_ml_config import BaseConfig
        
        # Define configuration classes
        @dataclass
        class ModelConfig(BaseConfig):
            num_layers: int
            hidden_size: int
            dropout_rate: float = 0.1
        
        @dataclass
        class TrainingConfig(BaseConfig):
            batch_size: int
            learning_rate: float
            num_epochs: int
            
        @dataclass
        class ExperimentConfig(BaseConfig):
            model: ModelConfig
            training: TrainingConfig
            experiment_name: str
            
        # Create a configuration from a dictionary
        exp_config = ExperimentConfig.from_dict({
            "model": {
                "num_layers": 3,
                "hidden_size": 256,
            },
            "training": {
                "batch_size": 32,
                "learning_rate": 0.001,
                "num_epochs": 10
            },
            "experiment_name": "experiment_001"
        })
        
        # Save to YAML
        exp_config.to_yaml("experiment_001.yaml")
        
        # Load from YAML
        loaded_config = ExperimentConfig.from_yaml("experiment_001.yaml")
        
        # Create a new configuration by inheriting from an existing one
        new_config = ExperimentConfig.inherit(
            exp_config,
            experiment_name="experiment_002",
            training=TrainingConfig(
                batch_size=64,
                learning_rate=0.0005,
                num_epochs=20
            )
        )
        ```

    Notes:
        - All nested configuration classes must inherit from BaseConfig
        - Optional nested configurations can be defined using `Optional[Config]` or `Config | None`
        - The class automatically handles nested configuration objects during serialization and deserialization
    """
    subconfigs: ClassVar[dict] = {}

    @staticmethod
    def get_baseconfig_type(field_type):
        """
        Extract a BaseConfig subclass type from a field type,
        handling cases like Optional[SomeConfig] and Union[SomeConfig, None]
        """
        # Check if it's directly a subclass of BaseConfig
        try:
            if isinstance(field_type, type) and issubclass(field_type, BaseConfig):
                return field_type
        except TypeError:
            # This happens if field_type is not a class
            pass
        
        # Check if it's a generic type (like Optional or Union)
        origin = get_origin(field_type)
        if origin is not None:
            # Handle cases like Optional[SomeConfig]
            if origin is Union or origin is types.UnionType:
                args = get_args(field_type)
                for arg in args:
                    config_type = BaseConfig.get_baseconfig_type(arg)
                    if config_type is not None:
                        return config_type
        
        return None

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register subconfigs based on type annotations
        """
        # This magic method is executed at definition time
        super().__init_subclass__(**kwargs)
        
        # Initialize subconfigs dictionary
        if 'subconfigs' not in cls.__dict__:
            cls.subconfigs = {}
        else:
            # If the class has its own subconfigs, use that as a starting point
            cls.subconfigs = cls.subconfigs.copy()
            
        # Get type hints for the class
        try:
            hints = get_type_hints(cls)
            
            # Inspect the type hints for BaseConfig types
            for field_name, field_type in hints.items():
                # Skip ClassVar fields
                if get_origin(field_type) is ClassVar:
                    continue
                
                config_type = cls.get_baseconfig_type(field_type)
                if config_type is not None:
                    cls.subconfigs[field_name] = config_type
        except (TypeError, ValueError):
            # This can happen if the class is not fully defined yet
            pass

    @classmethod
    def init_subconfig(cls, subconfig_name, subconfig_dict):
        """
        Initialize a subconfig from a dictionary
        """
        if subconfig_name not in cls.subconfigs:
            return subconfig_dict
        
        subconfig_cls = cls.subconfigs[subconfig_name]
        return subconfig_cls.from_dict(subconfig_dict)

    @classmethod
    def from_dict(cls, kwargs: dict):
        valid_keys = {f.name for f in fields(cls)}
        filtered_kwargs = {}
        for k, v in kwargs.items():
            if k not in valid_keys:
                continue
            if k in cls.subconfigs.keys():
                if v is None:
                    # Get field information to check if the field is optional
                    field_info = next((f for f in fields(cls) if f.name == k), None)
                    if field_info and (
                        field_info.default is not MISSING \
                        or field_info.default_factory is not MISSING
                        ):
                        # Field has a default value, so it's optional
                        filtered_kwargs[k] = None
                    else:
                        # Field is required
                        raise ValueError(f"Required subconfig '{k}' cannot be None")
                elif isinstance(v, dict):
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


def save_config(exp_config: ExampleExperimentConfig, time_id: str) -> None:
    "save config to yaml"
    import os

    os.makedirs("results/configs", exist_ok=True)
    exp_config.to_yaml(f"results/configs/exp_config_{time_id}.yaml")
