"""
A simple calculator module for demonstration purposes.
This module provides basic arithmetic operations.
"""


class Calculator:
    """A simple calculator class with basic arithmetic operations."""
    
    def add(self, a: float, b: float) -> float:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Sum of a and b
        """
        return a + b
    
    def subtract(self, a: float, b: float) -> float:
        """
        Subtract second number from first number.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Difference of a and b
        """
        return a - b
    
    def multiply(self, a: float, b: float) -> float:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
            
        Returns:
            Product of a and b
        """
        return a * b
    
    def divide(self, a: float, b: float) -> float:
        """
        Divide first number by second number.
        
        Args:
            a: Dividend
            b: Divisor
            
        Returns:
            Quotient of a and b
            
        Raises:
            ValueError: If divisor is zero
        """
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def power(self, base: float, exponent: float) -> float:
        """
        Raise base to the power of exponent.
        
        Args:
            base: Base number
            exponent: Exponent
            
        Returns:
            base raised to the power of exponent
        """
        return base ** exponent
    
    def square_root(self, number: float) -> float:
        """
        Calculate square root of a number.
        
        Args:
            number: Number to find square root of
            
        Returns:
            Square root of the number
            
        Raises:
            ValueError: If number is negative
        """
        if number < 0:
            raise ValueError("Cannot calculate square root of negative number")
        return number ** 0.5

