import pytest
import time
from app.utils.decorators import timing_decorator

def test_timing_decorator(capsys):
    """Test that the timing decorator correctly reports execution time."""
    # Arrange
    @timing_decorator
    def test_function():
        time.sleep(0.1)  # Sleep to ensure measurable execution time
        return "test result"
    
    # Act
    result = test_function()
    
    # Assert
    assert result == "test result"  # Function should return the original result
    
    # Check output
    captured = capsys.readouterr()
    assert "test_function executed in" in captured.out
    assert "seconds" in captured.out

@pytest.mark.parametrize("args,kwargs,expected", [
    ((1, 2), {}, 3),
    ((5,), {"y": 10}, 15),
    ((), {"x": 7, "y": 8}, 15)
])
def test_timing_decorator_with_arguments(args, kwargs, expected, capsys):
    """Test that the timing decorator works with different argument patterns."""
    # Arrange
    @timing_decorator
    def add(x=0, y=0):
        return x + y
    
    # Act
    result = add(*args, **kwargs)
    
    # Assert
    assert result == expected
    
    # Check output
    captured = capsys.readouterr()
    assert "add executed in" in captured.out

def test_timing_decorator_preserves_metadata():
    """Test that the timing decorator preserves function metadata."""
    # Arrange
    @timing_decorator
    def func_with_metadata():
        """Test docstring."""
        pass
    
    # Assert
    assert func_with_metadata.__name__ == "func_with_metadata"
    assert func_with_metadata.__doc__ == "Test docstring."
    
    # Ensure the wrapper is properly set as it would be by functools.wraps
    assert hasattr(func_with_metadata, "__wrapped__")
