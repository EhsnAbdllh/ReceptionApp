import os
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont
from config.settings import (
    PRINTER_NAME, MOKEB_NAME, AMOOD_NUMBER, CONTACT_PHONE,
    LABEL_WIDTH, LABEL_HEIGHT,
    FONT_PATH, FONT_SIZE_TITLE, FONT_SIZE_BODY, BASE_DIR
)
from utils.persian_utils import to_persian_digits
import jdatetime

class PrinterService:
    @staticmethod
    def generate_label_image(registrant):
        img = Image.new('RGB', (LABEL_WIDTH, LABEL_HEIGHT), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        try:
            font_title = ImageFont.truetype(str(FONT_PATH), FONT_SIZE_TITLE)
            font_body = ImageFont.truetype(str(FONT_PATH), FONT_SIZE_BODY)
        except IOError:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

        try:
            import arabic_reshaper
            from bidi.algorithm import get_display
            def prep_text(text):
                return get_display(arabic_reshaper.reshape(text))
        except ImportError:
            def prep_text(text):
                return text
        
        # Central 1700px logic
        # 3195 - 1700 = 1495, divided by 2 = 747.5
        left_margin = 747
        right_margin = left_margin + 1700
        
        right_x = right_margin - 50
        center_x = left_margin + 850
        left_x = left_margin + 50
        
        amood_str = to_persian_digits(f"عمود {AMOOD_NUMBER}")
        phone_str = to_persian_digits(f"تلفن: {CONTACT_PHONE}")
        
        d.text((right_x, 50), prep_text(MOKEB_NAME), font=font_title, fill=(0,0,0), anchor="ra")
        d.text((right_x, 150), prep_text(amood_str), font=font_body, fill=(0,0,0), anchor="ra")
        d.text((right_x, 220), prep_text(phone_str), font=font_body, fill=(0,0,0), anchor="ra")
        
        d.text((center_x, 80), prep_text(f"نام: {registrant.full_name}"), font=font_title, fill=(0,0,0), anchor="ma")
        d.text((center_x, 180), prep_text(f"موبایل: {to_persian_digits(registrant.phone_number)}"), font=font_body, fill=(0,0,0), anchor="ma")
        
        short_id = to_persian_digits(str(registrant.id).split('-')[0])
        time_str = to_persian_digits(registrant.registration_time)
        session_str = to_persian_digits(str(registrant.session.session_number))
        
        d.text((left_x, 50), prep_text(f"کد: {short_id}"), font=font_body, fill=(0,0,0), anchor="la")
        d.text((left_x, 120), prep_text(f"زمان ثبت: {time_str}"), font=font_body, fill=(0,0,0), anchor="la")
        d.text((left_x, 190), prep_text(f"سانس: {session_str}"), font=font_body, fill=(0,0,0), anchor="la")
        
        temp_path = BASE_DIR / "last_label.png"
        img.save(temp_path)
        return img, temp_path

    @staticmethod
    def print_label(registrant):
        img, temp_path = PrinterService.generate_label_image(registrant)
        printer_true_name = PrinterService.find_printer(PRINTER_NAME)
        try:
            hprinter = win32print.OpenPrinter(printer_true_name)
            try:
                hdc = win32ui.CreateDC()
                hdc.CreatePrinterDC(printer_true_name)
                hdc.StartDoc('Label Print')
                hdc.StartPage()
                
                from PIL import ImageWin
                dib = ImageWin.Dib(img)
                dib.draw(hdc.GetHandleOutput(), (0, 0, LABEL_WIDTH, LABEL_HEIGHT))
                
                hdc.EndPage()
                hdc.EndDoc()
                hdc.DeleteDC()
            finally:
                win32print.ClosePrinter(hprinter)
        except Exception as e:
            raise RuntimeError(f"خطا در ارتباط با پرینتر: {e}")

    @staticmethod
    def find_printer(target_name):
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = win32print.EnumPrinters(flags)
        target_name_lower = target_name.lower()

        for printer in printers:
            printer_name = printer[2]
            if target_name_lower in printer_name.lower():
                return printer_name
        return None
