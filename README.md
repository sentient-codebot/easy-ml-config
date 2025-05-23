# easy-ml-config

Super lightweight library to provide a simple base configuration class to maintain consistency and reproducibility for machine learning projects. 
There is only one module `ml_config.configuration` that contains the `BaseConfig` class, which allows you to:
- Define complex and nested configuration classes. 
- Export/Import your configuration to a dictionary or a yaml file with simply `to_dict()`, `from_dict`, `to_yaml` and `from_yaml`. 


```python
from dataclasses import dataclass
from easy_ml_config import BaseConfig

@dataclass
class ValidationConfig(BaseConfig):
    batch_size: int
    upload_to_server: bool = False

@dataclass
class TrainConfig(BaseConfig):
    num_epochs: int
    batch_size: int
    learning_rate: float
    validation_config: ValidationConfig | None = None

class ModelConfig(BaseConfig):
    num_layer: int

@dataclass
class MyExpConfig(BaseConfig):
    model: MyModelConfig
    train: TrainConfig
    exp_id: str

# Initialize from a dictionary
exp_config = MyExpConfig.from_dict({
    "model": {
        "num_layer": 3,
    },
    "train": {
        "num_epochs": 10,
        "batch_size": 32,
        "learning_rate": 0.001,
        "validation_config": {
            "batch_size": 16,
            "upload_to_server": False
        } # optional
    },
    "exp_id": "exp_1"
})

# Export to a yaml file
exp_config.to_yaml("exp_config_001.yaml")

# Initialize from a yaml file
exp_config = MyExpConfig.from_yaml("exp_config_001.yaml")
```
The yaml file will look like this:
```yaml
model:
    num_layer: 3
train:
    num_epochs: 10
    batch_size: 32
    learning_rate: 0.001
    validation_config:
        batch_size: 16
        upload_to_server: false
exp_id: exp_1
```

## Installation
```bash
pip install easy-ml-config
```

## Usage

Start with defining your own configuration by inheriting from `BaseConfig`. Once you have that, you can utilize all the predefined functionalities of `BaseConfig`.

### Define Your Configuration

```python
from dataclasses import dataclass

from easy_ml_config import BaseConfig


@dataclass
class MyModelConfig(BaseConfig):
    num_layer: int

@dataclass
class MyExpConfig(BaseConfig):
    model: MyModelConfig
    batch_size: int
    learning_rate: float
```

### Instantiate Your Configuration
When you are running an experiment with a specific settings. Initialize your configurations. 

#### Initialize from A Dictionary

```python
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

#### Initialize from A YAML File

```yaml
# config.yaml
model:
  num_layer: 3
batch_size: 32
learning_rate: 0.001
```

```python
config = MyExpConfig.from_yaml("config.yaml")
```

### Output Your Configuration
Often you might want to save your configuration to a file. You can do that easily with the `to_dict` and `to_yaml` methods. 

```python
# Save to a dictionary
config_dict = config.to_dict()
# Save to a yaml file
config.to_yaml("config.yaml")
```
The exported dictionary and yaml file can be directly used again to recreate the Configurations.
```python
# Load from a dictionary
config = MyExpConfig.from_dict(config_dict)
# Load from a yaml file
config = MyExpConfig.from_yaml("config.yaml")
```
