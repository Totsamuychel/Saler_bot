"""Fuel price calculator"""
import config

def calculate_price(liters: int) -> int:
    """
    Calculates the total fuel cost.

    Args:
        liters: Number of liters

    Returns:
           Total cost in hryvnias
    """
    if liters >= config.WHOLESALE_THRESHOLD:
        price_per_liter = config.WHOLESALE_PRICE
    else:
        price_per_liter = config.RETAIL_PRICE
    
    return price_per_liter * liters

def get_price_per_liter(liters: int) -> int:
    """
    Returns the price per liter based on quantity
    
    Args:
        liters: Number of liters
        
    Returns:
        Price per liter in hryvnia
    """
    if liters >= config.WHOLESALE_THRESHOLD:
        return config.WHOLESALE_PRICE
    else:
        return config.RETAIL_PRICE

def is_wholesale(liters: int) -> bool:
    """
    Checks if the purchase is wholesale
    
    Args:
        liters: Number of liters
        
    Returns:
        True if wholesale, False if retail
    """
    return liters >= config.WHOLESALE_THRESHOLD

def calculate_savings(liters: int) -> int:
    """
    Calculates savings when buying in bulk
    
    Args:
        liters: Number of liters
        
    Returns:
        Amount of savings in hryvnias
    """
    if not is_wholesale(liters):
        return 0
    
    retail_total = config.RETAIL_PRICE * liters
    wholesale_total = config.WHOLESALE_PRICE * liters
    
    return retail_total - wholesale_total
