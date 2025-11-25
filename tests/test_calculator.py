"""
Unit tests for the Calculator module.
These tests will be run by Jenkins during the Python Unit Tests stage.
"""

import pytest
from calculator import Calculator


class TestCalculator:
    """Test suite for Calculator class."""
    
    def setup_method(self):
        """Set up test fixtures - runs before each test method."""
        self.calc = Calculator()
    
    def test_add_positive_numbers(self):
        """Test addition of positive numbers."""
        assert self.calc.add(5, 3) == 8
        assert self.calc.add(10, 20) == 30
        assert self.calc.add(0, 5) == 5
    
    def test_add_negative_numbers(self):
        """Test addition of negative numbers."""
        assert self.calc.add(-5, -3) == -8
        assert self.calc.add(-10, 5) == -5
        assert self.calc.add(5, -3) == 2
    
    def test_add_decimal_numbers(self):
        """Test addition of decimal numbers."""
        assert self.calc.add(2.5, 3.7) == 6.2
        assert self.calc.add(0.1, 0.2) == pytest.approx(0.3)
    
    def test_subtract_positive_numbers(self):
        """Test subtraction of positive numbers."""
        assert self.calc.subtract(10, 3) == 7
        assert self.calc.subtract(5, 5) == 0
        assert self.calc.subtract(3, 10) == -7
    
    def test_subtract_negative_numbers(self):
        """Test subtraction with negative numbers."""
        assert self.calc.subtract(-5, -3) == -2
        assert self.calc.subtract(-10, 5) == -15
        assert self.calc.subtract(5, -3) == 8
    
    def test_multiply_positive_numbers(self):
        """Test multiplication of positive numbers."""
        assert self.calc.multiply(5, 3) == 15
        assert self.calc.multiply(10, 0) == 0
        assert self.calc.multiply(4, 2.5) == 10.0
    
    def test_multiply_negative_numbers(self):
        """Test multiplication with negative numbers."""
        assert self.calc.multiply(-5, 3) == -15
        assert self.calc.multiply(-5, -3) == 15
        assert self.calc.multiply(5, -3) == -15
    
    def test_divide_positive_numbers(self):
        """Test division of positive numbers."""
        assert self.calc.divide(10, 2) == 5.0
        assert self.calc.divide(15, 3) == 5.0
        assert self.calc.divide(7, 2) == 3.5
    
    def test_divide_negative_numbers(self):
        """Test division with negative numbers."""
        assert self.calc.divide(-10, 2) == -5.0
        assert self.calc.divide(10, -2) == -5.0
        assert self.calc.divide(-10, -2) == 5.0
    
    def test_divide_by_zero_raises_error(self):
        """Test that dividing by zero raises ValueError."""
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
        
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            self.calc.divide(-5, 0)
    
    def test_power_positive_numbers(self):
        """Test power operation with positive numbers."""
        assert self.calc.power(2, 3) == 8
        assert self.calc.power(5, 2) == 25
        assert self.calc.power(10, 0) == 1
        assert self.calc.power(2, 0.5) == pytest.approx(1.414, rel=1e-2)
    
    def test_power_negative_base(self):
        """Test power operation with negative base."""
        assert self.calc.power(-2, 2) == 4
        assert self.calc.power(-2, 3) == -8
    
    def test_square_root_positive_numbers(self):
        """Test square root of positive numbers."""
        assert self.calc.square_root(4) == 2.0
        assert self.calc.square_root(9) == 3.0
        assert self.calc.square_root(16) == 4.0
        assert self.calc.square_root(25) == 5.0
        assert self.calc.square_root(0) == 0.0
    
    def test_square_root_decimal_numbers(self):
        """Test square root of decimal numbers."""
        assert self.calc.square_root(2.25) == 1.5
        assert self.calc.square_root(0.25) == 0.5
    
    def test_square_root_negative_number_raises_error(self):
        """Test that square root of negative number raises ValueError."""
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            self.calc.square_root(-4)
        
        with pytest.raises(ValueError, match="Cannot calculate square root of negative number"):
            self.calc.square_root(-1)

