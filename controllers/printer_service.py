import os
import win32print
import win32ui
from PIL import Image, ImageDraw, ImageFont
from config.settings import (
    PRINTER_NAME, MOKEB_NAME, AMOOD_NUMBER, CONTACT_PHONE,
    LABEL_WIDTH, LABEL_HEIGHT,
    FONT_PATH, FONT_SIZE_TITLE, FONT_SIZE_BODY, BASE_DIR,
    WRISTBAND_SHIFT_OFFSET
)
from utils.persian_utils import to_persian_digits
import jdatetime

class PrinterService:
    @staticmethod
    def generate_label_image(registrant):
        img = Image.new('RGB', (LABEL_WIDTH, LABEL_HEIGHT), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        try:
            # Scale sizes to 32 and 24 to match the neatness of test_wristband, but optimized for Vazirmatn
            font_title = ImageFont.truetype(str(FONT_PATH), 32)
            font_body = ImageFont.truetype(str(FONT_PATH), 24)
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
        
        # Dimensions for 8 cm text area (8 cm / 2.54 cm/inch * 300 DPI = 945 pixels)
        print_area_size = 945
        left_margin = (LABEL_WIDTH - print_area_size) // 2 + WRISTBAND_SHIFT_OFFSET
        right_margin = left_margin + print_area_size
        
        # Draw minimal diagonal hatching (هاشور) in the blank margins
        # Leaving 2 cm blank (236 pixels) at the start and end, and keeping lines inside the 12px and 288px vertical boundaries
        left_hatch_start = 236
        right_hatch_end = LABEL_WIDTH - 236
        hatch_spacing = 50
        
        # Left margin hatching
        for x in range(left_hatch_start - LABEL_HEIGHT, left_margin, hatch_spacing):
            x1_clipped = left_hatch_start if x < left_hatch_start else x
            y1_clipped = left_hatch_start - x if x < left_hatch_start else 0
            
            # Clip y1 to at least 12px top margin
            if y1_clipped < 12:
                x1_clipped = 12 + x
                y1_clipped = 12
            
            x2_clipped = x + LABEL_HEIGHT
            y2_clipped = LABEL_HEIGHT
            if x2_clipped > left_margin:
                x2_clipped = left_margin
                y2_clipped = left_margin - x
                
            # Clip y2 to at most 288px bottom margin
            if y2_clipped > 288:
                x2_clipped = 288 + x
                y2_clipped = 288
                
            if y1_clipped < y2_clipped and x1_clipped < x2_clipped:
                d.line([(x1_clipped, y1_clipped), (x2_clipped, y2_clipped)], fill=(0, 0, 0), width=1)
                
        # Right margin hatching
        for x in range(right_margin - LABEL_HEIGHT, right_hatch_end, hatch_spacing):
            x1_clipped = right_margin if x < right_margin else x
            y1_clipped = right_margin - x if x < right_margin else 0
            
            # Clip y1 to at least 12px top margin
            if y1_clipped < 12:
                x1_clipped = 12 + x
                y1_clipped = 12
            
            x2_clipped = x + LABEL_HEIGHT
            y2_clipped = LABEL_HEIGHT
            if x2_clipped > right_hatch_end:
                x2_clipped = right_hatch_end
                y2_clipped = right_hatch_end - x
                
            # Clip y2 to at most 288px bottom margin
            if y2_clipped > 288:
                x2_clipped = 288 + x
                y2_clipped = 288
                
            if y1_clipped < y2_clipped and x1_clipped < x2_clipped:
                d.line([(x1_clipped, y1_clipped), (x2_clipped, y2_clipped)], fill=(0, 0, 0), width=1)
        
        # 1. Outer Border of the 8 cm text area (width=2 for minimal style, inset to y=12 and y=288)
        d.rectangle([left_margin, 12, right_margin, LABEL_HEIGHT-12], outline=(0, 0, 0), width=2)
        
        # Vertical divider lines inside the 8 cm area (proportional splits, width=1, inset to y=12 and y=288)
        line2 = left_margin + 305   # divider between Section 3 (left) and Section 2 (middle)
        line1 = line2 + 335         # divider between Section 2 (middle) and Section 1 (right)
        d.line([(line1, 12), (line1, LABEL_HEIGHT-12)], fill=(0, 0, 0), width=1)
        d.line([(line2, 12), (line2, LABEL_HEIGHT-12)], fill=(0, 0, 0), width=1)
        
        # 2. Section 1 (Right): Mokeb & Amood details (static info)
        center_top = line1 + (right_margin - line1) // 2
        amood_str = to_persian_digits(AMOOD_NUMBER) if "عمود" in AMOOD_NUMBER else to_persian_digits(f"عمود {AMOOD_NUMBER}")
        
        logo_path = BASE_DIR.parent / "لوگوی جزیره امید.jpg"
        logo_drawn = False
        if logo_path.exists():
            try:
                logo_img = Image.open(logo_path)
                # Resize the logo to fit Section 1 larger (160x160 px)
                logo_resized = logo_img.resize((160, 160), Image.Resampling.LANCZOS)
                # Calculate paste position (centered horizontally at center_top, and Y starting at 25)
                logo_x = int(center_top - 80)
                logo_y = 25
                img.paste(logo_resized, (logo_x, logo_y))
                logo_drawn = True
            except Exception as e:
                print(f"[PRINTER DEBUG] Error loading or pasting logo: {e}")
                
        # If the logo couldn't be drawn, fall back to the text title
        if not logo_drawn:
            d.text((center_top, 100), prep_text(MOKEB_NAME), font=font_title, fill=(0,0,0), anchor="mm")
            d.text((center_top, 210), prep_text(amood_str), font=font_body, fill=(0,0,0), anchor="mm")
        else:
            d.text((center_top, 236), prep_text(amood_str), font=font_body, fill=(0,0,0), anchor="mm")
        
        # 3. Section 2 (Middle): Registrant details (dynamic info)
        center_middle = line2 + (line1 - line2) // 2
        
        name_text = f"نام کودک: {registrant.full_name}"
        phone_text = f"تلفن همراه: {to_persian_digits(registrant.phone_number)}"
        
        # Extract time portion (HH:MM) from registration_time
        time_part = registrant.registration_time.split(' ')[-1] if ' ' in registrant.registration_time else registrant.registration_time
        time_text = f"ساعت ورود: {to_persian_digits(time_part)}"
        
        session_text = f"سانس ورود: {to_persian_digits(str(registrant.session.session_number))}"
        
        d.text((center_middle, 60), prep_text(name_text), font=font_body, fill=(0,0,0), anchor="mm")
        d.text((center_middle, 120), prep_text(phone_text), font=font_body, fill=(0,0,0), anchor="mm")
        d.text((center_middle, 180), prep_text(time_text), font=font_body, fill=(0,0,0), anchor="mm")
        d.text((center_middle, 240), prep_text(session_text), font=font_body, fill=(0,0,0), anchor="mm")
        
        # 4. Section 3 (Left): Date, Registrant ID / Code, and Contact Phone
        center_bottom = left_margin + (line2 - left_margin) // 2
        
        # Load custom font sizes for Section 3 to fit the 305px width perfectly
        try:
            font_date = ImageFont.truetype(str(FONT_PATH), 22)
            font_code = ImageFont.truetype(str(FONT_PATH), 28)
            font_contact_title = ImageFont.truetype(str(FONT_PATH), 20)
            font_contact_phone = ImageFont.truetype(str(FONT_PATH), 22)
        except IOError:
            font_date = font_body
            font_code = font_title
            font_contact_title = font_body
            font_contact_phone = font_body
            
        today_shamsi = jdatetime.date.today().strftime("%Y/%m/%d")
        date_text = to_persian_digits(f"تاریخ: {today_shamsi}")
        
        short_id = to_persian_digits(str(registrant.id).split('-')[0])
        code_text = to_persian_digits(f"کد پذیرش: {short_id}")
        
        contact_title_text = "تماس مسئول موکب"
        contact_phone_text = to_persian_digits(CONTACT_PHONE)
        
        d.text((center_bottom, 55), prep_text(date_text), font=font_date, fill=(0,0,0), anchor="mm")
        d.text((center_bottom, 120), prep_text(code_text), font=font_code, fill=(0,0,0), anchor="mm")
        d.text((center_bottom, 190), prep_text(contact_title_text), font=font_contact_title, fill=(0,0,0), anchor="mm")
        d.text((center_bottom, 245), prep_text(contact_phone_text), font=font_contact_phone, fill=(0,0,0), anchor="mm")
        
        temp_path = BASE_DIR / "last_label.png"
        img.save(temp_path)
        return img, temp_path

    @staticmethod
    def find_label_printer(target_name):
        try:
            flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
            printers = win32print.EnumPrinters(flags)
            target_name_clean = target_name.lower().strip()
            
            print("[PRINTER DEBUG] Listing all detected printers on system:")
            for printer in printers:
                print(f"  - '{printer[2]}'")
            
            # First pass: check for an EXACT match (case-insensitive & stripped)
            for printer in printers:
                printer_name_clean = printer[2].lower().strip()
                if target_name_clean == printer_name_clean:
                    return printer[2]
                    
            # Second pass: check for a substring match (fallback)
            for printer in printers:
                printer_name_clean = printer[2].lower().strip()
                if target_name_clean in printer_name_clean:
                    return printer[2]
        except Exception as e:
            print(f"[PRINTER DEBUG] Error enumerating printers: {e}")
        return None

    @staticmethod
    def print_label(registrant):
        img, temp_path = PrinterService.generate_label_image(registrant)
        
        # Search for the printer containing the target name
        print(f"\n[PRINTER DEBUG] Configured Target: '{PRINTER_NAME}'")
        actual_printer_name = PrinterService.find_label_printer(PRINTER_NAME)
        print(f"[PRINTER DEBUG] Resolved Name on System: '{actual_printer_name}'")
        
        if not actual_printer_name:
            raise RuntimeError(f"پرینتری با نام شامل '{PRINTER_NAME}' در سیستم پیدا نشد. لطفاً نام پرینتر را در فایل تنظیمات بررسی کنید.")
            
        try:
            print("[PRINTER DEBUG] Initializing GDI Device Context (DC)...")
            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(actual_printer_name)
            hdc.StartDoc('Label Print')
            hdc.StartPage()
            
            from PIL import ImageWin
            rotated_img = img.rotate(90, expand=True)
            dib = ImageWin.Dib(rotated_img)
            dib.draw(hdc.GetHandleOutput(), (0, 0, LABEL_HEIGHT, LABEL_WIDTH))
            
            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()
            print("[PRINTER DEBUG] Print job sent successfully to win32 spooler!")
        except Exception as e:
            raise RuntimeError(f"خطا در ارتباط با پرینتر ({actual_printer_name}): {e}")

