import pytest
from dataclasses import dataclass
from typing import Optional, List, Dict, Union

# Import the BaseConfig from our implementation
# For testing purposes, you might need to adjust the import path
from easy_ml_config.configuration import BaseConfig

# Define test configuration classes
@dataclass
class NestedConfig(BaseConfig):
    value: int
    name: str

@dataclass
class DeepNestedConfig(BaseConfig):
    id: str
    nested: NestedConfig

@dataclass
class OptionalConfig(BaseConfig):
    required: str
    optional_nested: Optional[NestedConfig] = None

@dataclass
class ComplexConfig(BaseConfig):
    name: str
    nested_config: NestedConfig
    deep_nested: DeepNestedConfig
    # optional_config: Optional[OptionalConfig] = None
    optional_config: OptionalConfig | None = None
    value_list: list[int] | None = None
    value_dict: Dict[str, float] | None = None

# Tests
def test_automatic_subconfig_registration():
    """Test that subconfigs are automatically registered based on type annotations."""
    assert "nested_config" in ComplexConfig.subconfigs
    assert ComplexConfig.subconfigs["nested_config"] == NestedConfig
    
    assert "deep_nested" in ComplexConfig.subconfigs
    assert ComplexConfig.subconfigs["deep_nested"] == DeepNestedConfig
    
    assert "optional_config" in ComplexConfig.subconfigs
    assert ComplexConfig.subconfigs["optional_config"] == OptionalConfig
    
    assert "nested" in DeepNestedConfig.subconfigs
    assert DeepNestedConfig.subconfigs["nested"] == NestedConfig
    
    assert "optional_nested" in OptionalConfig.subconfigs
    assert OptionalConfig.subconfigs["optional_nested"] == NestedConfig

def test_from_dict_basic():
    """Test basic dictionary to config conversion."""
    config_dict = {"value": 42, "name": "test"}
    config = NestedConfig.from_dict(config_dict)
    
    assert config.value == 42
    assert config.name == "test"

def test_from_dict_nested():
    """Test nested dictionary to config conversion."""
    config_dict = {
        "name": "complex",
        "nested_config": {"value": 42, "name": "nested"},
        "deep_nested": {
            "id": "deep1",
            "nested": {"value": 99, "name": "deep_nested"}
        }
    }
    
    config = ComplexConfig.from_dict(config_dict)
    
    assert config.name == "complex"
    assert isinstance(config.nested_config, NestedConfig)
    assert config.nested_config.value == 42
    assert config.nested_config.name == "nested"
    assert isinstance(config.deep_nested, DeepNestedConfig)
    assert config.deep_nested.id == "deep1"
    assert isinstance(config.deep_nested.nested, NestedConfig)
    assert config.deep_nested.nested.value == 99
    assert config.deep_nested.nested.name == "deep_nested"

def test_from_dict_optional_fields():
    """Test handling of optional fields."""
    # Without optional field
    config_dict = {
        "name": "complex",
        "nested_config": {"value": 42, "name": "nested"},
        "deep_nested": {
            "id": "deep1",
            "nested": {"value": 99, "name": "deep_nested"}
        }
    }
    
    config = ComplexConfig.from_dict(config_dict)
    assert config.optional_config is None
    
    # With optional field
    config_dict["optional_config"] = {
        "required": "required_value",
        "optional_nested": {"value": 123, "name": "optional_nested"}
    }
    
    config = ComplexConfig.from_dict(config_dict)
    assert isinstance(config.optional_config, OptionalConfig)
    assert config.optional_config.required == "required_value"
    assert isinstance(config.optional_config.optional_nested, NestedConfig)
    assert config.optional_config.optional_nested.value == 123

def test_from_dict_with_extra_fields():
    """Test that extra fields in the dictionary are ignored."""
    config_dict = {
        "value": 42, 
        "name": "test",
        "extra_field": "should be ignored"
    }
    
    config = NestedConfig.from_dict(config_dict)
    assert config.value == 42
    assert config.name == "test"
    assert not hasattr(config, "extra_field")

def test_to_dict_basic():
    """Test basic config to dictionary conversion."""
    config = NestedConfig(value=42, name="test")
    config_dict = config.to_dict()
    
    assert config_dict == {"value": 42, "name": "test"}

def test_to_dict_nested():
    """Test nested config to dictionary conversion."""
    nested = NestedConfig(value=42, name="nested")
    deep_nested = DeepNestedConfig(
        id="deep1",
        nested=NestedConfig(value=99, name="deep_nested")
    )
    
    config = ComplexConfig(
        name="complex",
        nested_config=nested,
        deep_nested=deep_nested
    )
    
    config_dict = config.to_dict()
    
    expected = {
        "name": "complex",
        "nested_config": {"value": 42, "name": "nested"},
        "deep_nested": {
            "id": "deep1",
            "nested": {"value": 99, "name": "deep_nested"}
        },
        "optional_config": None,
        "value_list": None,
        "value_dict": None
    }
    
    assert config_dict == expected

def test_round_trip():
    """Test that converting from dict to config and back to dict preserves the structure."""
    original_dict = {
        "name": "complex",
        "nested_config": {"value": 42, "name": "nested"},
        "deep_nested": {
            "id": "deep1",
            "nested": {"value": 99, "name": "deep_nested"}
        },
        "optional_config": {
            "required": "required_value",
            "optional_nested": {"value": 123, "name": "optional_nested"}
        },
        "value_list": [1, 2, 3],
        "value_dict": {"a": 1.0, "b": 2.0}
    }
    
    # Convert to config
    config = ComplexConfig.from_dict(original_dict)
    
    # Convert back to dict
    result_dict = config.to_dict()
    
    # Check that the result matches the original
    assert result_dict == original_dict

def test_inherit():
    """Test the inherit method for creating derived configs."""
    parent = ComplexConfig(
        name="parent",
        nested_config=NestedConfig(value=42, name="nested"),
        deep_nested=DeepNestedConfig(
            id="deep1",
            nested=NestedConfig(value=99, name="deep_nested")
        )
    )
    
    # Create a child config with some overrides
    child = ComplexConfig.inherit(
        parent,
        name="child",
        nested_config=NestedConfig(value=84, name="child_nested")
    )
    
    # Check that overridden values were updated
    assert child.name == "child"
    assert child.nested_config.value == 84
    assert child.nested_config.name == "child_nested"
    
    # Check that non-overridden values were preserved
    assert child.deep_nested.id == "deep1"
    assert child.deep_nested.nested.value == 99

def test_inherit_with_none():
    """Test the inherit method when explicitly setting a subconfig to None."""
    parent = ComplexConfig(
        name="parent",
        nested_config=NestedConfig(value=42, name="nested"),
        deep_nested=DeepNestedConfig(
            id="deep1",
            nested=NestedConfig(value=99, name="deep_nested")
        ),
        optional_config=OptionalConfig(
            required="parent_required",
            optional_nested=NestedConfig(value=100, name="parent_optional")
        )
    )
    
    # Create a child config with some overrides, including setting optional_config to None
    child = ComplexConfig.inherit(
        parent,
        name="child",
        optional_config=None
    )
    
    # Check that overridden values were updated
    assert child.name == "child"
    assert child.optional_config is None
    
    # Check that non-overridden values were preserved
    assert child.nested_config.value == 42
    assert child.deep_nested.id == "deep1"

def test_from_dict_with_none_required_field():
    """Test behavior when a required subconfig is explicitly set to None."""
    config_dict = {
        "name": "complex",
        "nested_config": None,  # This is a required field
        "deep_nested": {
            "id": "deep1",
            "nested": {"value": 99, "name": "deep_nested"}
        }
    }
    
    # This should raise a ValueError because nested_config is required
    with pytest.raises(ValueError):
        ComplexConfig.from_dict(config_dict)

def test_inherit_with_none_required_field():
    """Test the inherit method when setting a required subconfig to None."""
    parent = ComplexConfig(
        name="parent",
        nested_config=NestedConfig(value=42, name="nested"),
        deep_nested=DeepNestedConfig(
            id="deep1",
            nested=NestedConfig(value=99, name="deep_nested")
        )
    )
    
    # This should raise a ValueError because nested_config is required
    with pytest.raises(ValueError):
        ComplexConfig.inherit(
            parent,
            nested_config=None
        )