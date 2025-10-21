"""Генератор QR-кодов для талонов"""
import qrcode
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

async def generate_qr_code(talon_id: int) -> str:
    """
    Генерирует QR-код для талона
    
    Args:
        talon_id: ID талона
        
    Returns:
        Путь к файлу с QR-кодом
    """
    try:
        # Создаем директорию для QR-кодов если её нет
        qr_dir = "qr_codes"
        if not os.path.exists(qr_dir):
            os.makedirs(qr_dir)
        
        # Данные для QR-кода
        qr_data = f"TALON_{talon_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем файл
        filename = f"talon_{talon_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(qr_dir, filename)
        img.save(filepath)
        
        logger.info(f"QR code generated for talon {talon_id}: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error generating QR code for talon {talon_id}: {e}")
        return ""

def cleanup_old_qr_codes(days_old: int = 30):
    """
    Удаляет старые QR-коды
    
    Args:
        days_old: Возраст файлов в днях для удаления
    """
    try:
        qr_dir = "qr_codes"
        if not os.path.exists(qr_dir):
            return
        
        current_time = datetime.now()
        
        for filename in os.listdir(qr_dir):
            filepath = os.path.join(qr_dir, filename)
            
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                age = (current_time - file_time).days
                
                if age > days_old:
                    os.remove(filepath)
                    logger.info(f"Removed old QR code: {filepath}")
                    
    except Exception as e:
        logger.error(f"Error cleaning up QR codes: {e}")