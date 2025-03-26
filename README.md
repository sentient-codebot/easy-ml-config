# ml-config

Super lightweight library to provide a simple base configuration class for machine learning projects. 
There is only one module `ml_config.configuration` that contains the `BaseConfig` class. 

## Features

- Support for nested configurations
- Hassle-free configuration initialization from nested dictionary and yaml file. 
- Hassle-free configuration output to dictionary and yaml file. 

## Installation
```bash
pip install ml-config
```

## Usage
```python
from dataclasses import dataclass

from ml_config import BaseConfig


@dataclass
class MyModelConfig(BaseConfig):
    num_layer: int

@dataclass
class MyExpConfig(BaseConfig):
    model: MyModelConfig
    batch_size: int
    learning_rate: float

    subconfigs: ClassVar[dict] = {
        "model": MyModelConfig,
    }

    @classmethod
    def init_subconfig(cls, subconfig_name, subconfig_dict) -> BaseConfig | dict:
        if subconfig_name not in cls.subconfigs:
            return subconfig_dict
        if subconfig_name == "model":
            return MyModelConfig.from_dict(subconfig_dict)

def main():
    nested_args = {
        "model": {
            "num_layer": 3,
        },
        "batch_size": 32,
        "learning_rate": 0.001,
    }
    config = MyExpConfig.from_dict(nested_args)
    # model = MyModel(num_layer=config.model.num_layer)

if __name__ == "__main__":
    main()
```

