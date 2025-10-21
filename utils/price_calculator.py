"""Калькулятор цен на топливо"""
import config

def calculate_price(liters: int) -> int:
    """
    Рассчитывает общую стоимость топлива
    
    Args:
        liters: Количество литров
        
    Returns:
        Общая стоимость в гривнах
    """
    if liters >= config.WHOLESALE_THRESHOLD:
        price_per_liter = config.WHOLESALE_PRICE
    else:
        price_per_liter = config.RETAIL_PRICE
    
    return price_per_liter * liters

def get_price_per_liter(liters: int) -> int:
    """
    Возвращает цену за литр в зависимости от количества
    
    Args:
        liters: Количество литров
        
    Returns:
        Цена за литр в гривнах
    """
    if liters >= config.WHOLESALE_THRESHOLD:
        return config.WHOLESALE_PRICE
    else:
        return config.RETAIL_PRICE

def is_wholesale(liters: int) -> bool:
    """
    Проверяет, является ли покупка оптовой
    
    Args:
        liters: Количество литров
        
    Returns:
        True если оптовая покупка, False если розничная
    """
    return liters >= config.WHOLESALE_THRESHOLD

def calculate_savings(liters: int) -> int:
    """
    Рассчитывает экономию при оптовой покупке
    
    Args:
        liters: Количество литров
        
    Returns:
        Сумма экономии в гривнах
    """
    if not is_wholesale(liters):
        return 0
    
    retail_total = config.RETAIL_PRICE * liters
    wholesale_total = config.WHOLESALE_PRICE * liters
    
    return retail_total - wholesale_total