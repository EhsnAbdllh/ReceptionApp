import re
import jdatetime
from models.registrant import Registrant
from controllers.session_manager import SessionManager
from controllers.printer_service import PrinterService

class RegistrationManager:
    @staticmethod
    def validate_phone(phone):
        if not phone:
            return False
        # Normalize digits and strip spaces/dashes
        from utils.persian_utils import to_english_digits
        phone = to_english_digits(phone).strip()
        phone_clean = re.sub(r'[\s\-()]+', '', phone)
        # Allows optional leading '+' followed by 5 to 15 digits
        pattern = r'^\+?\d{5,15}$'
        return bool(re.match(pattern, phone_clean))

    @staticmethod
    def validate_name(name):
        return bool(name and 2 < len(name.strip()) <= 24)

    @staticmethod
    def register(full_name, phone_number, session, print_lang="fa"):
        if not session:
            return False, "سانس فعالی یافت نشد."
        
        if not RegistrationManager.validate_name(full_name):
            return False, "نام وارد شده نامعتبر است. (نام باید بین ۳ تا ۲۴ کاراکتر باشد)"

        # Clean and normalize phone number
        if phone_number:
            from utils.persian_utils import to_english_digits
            phone_number = to_english_digits(phone_number).strip()
            phone_number = re.sub(r'[\s\-()]+', '', phone_number)
            
        if not RegistrationManager.validate_phone(phone_number):
            return False, "شماره موبایل نامعتبر است. (مثال: 09123456789 یا +964...)"

        # Check if the session's time is over
        now = jdatetime.datetime.now()
        try:
            s_end = jdatetime.datetime.strptime(session.end_time, "%Y/%m/%d %H:%M")
        except Exception:
            return False, "زمان پایان سانس نامعتبر است."
            
        if now > s_end:
            return False, "زمان این سانس به پایان رسیده است و امکان ثبت‌نام در آن وجود ندارد."

        remaining = SessionManager.get_remaining_capacity(session)
        if remaining <= 0:
            return False, "ظرفیت سانس پر شده است."
            
        now_str = now.strftime("%Y/%m/%d %H:%M")
        import uuid
        # Generate a UUID whose first 4 characters are unique in the database
        while True:
            u = uuid.uuid4()
            prefix = str(u)[:4].lower()
            collision = Registrant.select().where(Registrant.id.cast('text').startswith(prefix)).exists()
            if not collision:
                break

        try:
            reg = Registrant.create(
                id=u,
                full_name=full_name,
                phone_number=phone_number,
                registration_time=now_str,
                session=session
            )
            try:
                PrinterService.print_label(reg, lang=print_lang)
            except Exception as e:
                return True, f"ثبت نام با موفقیت انجام شد، اما در چاپ خطا رخ داد:\n{str(e)}"
            
            return True, "ثبت نام با موفقیت انجام شد."
        except Exception as e:
            return False, f"خطا در ذخیره اطلاعات: {str(e)}"

    @staticmethod
    def update_registrant(registrant_id, new_name, new_phone):
        if not RegistrationManager.validate_name(new_name):
            return False, "نام وارد شده نامعتبر است. (نام باید بین ۳ تا ۲۴ کاراکتر باشد)"

        # Clean and normalize phone number
        if new_phone:
            from utils.persian_utils import to_english_digits
            new_phone = to_english_digits(new_phone).strip()
            new_phone = re.sub(r'[\s\-()]+', '', new_phone)

        if not RegistrationManager.validate_phone(new_phone):
            return False, "شماره موبایل نامعتبر است. (مثال: 09123456789 یا +964...)"
            
        try:
            reg = Registrant.get_by_id(registrant_id)
            reg.full_name = new_name
            reg.phone_number = new_phone
            reg.save()
            return True, "اطلاعات با موفقیت بروزرسانی شد."
        except Exception as e:
            return False, f"خطا در بروزرسانی اطلاعات: {str(e)}"

    @staticmethod
    def delete_registrant(registrant_id):
        try:
            Registrant.delete().where(Registrant.id == registrant_id).execute()
            return True, "ثبت‌نام با موفقیت حذف شد."
        except Exception as e:
            return False, f"خطا در حذف اطلاعات: {str(e)}"
