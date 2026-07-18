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
        # Iranian mobile format: 11 digits, starts with 09
        pattern = r'^09\d{9}$'
        return bool(re.match(pattern, phone))

    @staticmethod
    def validate_name(name):
        return bool(name and len(name.strip()) > 2)

    @staticmethod
    def register(full_name, phone_number, session, print_lang="fa"):
        if not session:
            return False, "سانس فعالی یافت نشد."
        
        if not RegistrationManager.validate_name(full_name):
            return False, "نام وارد شده نامعتبر است."

        if not RegistrationManager.validate_phone(phone_number):
            return False, "شماره موبایل نامعتبر است. (مثال: 09123456789)"

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
            return False, "نام وارد شده نامعتبر است."

        if not RegistrationManager.validate_phone(new_phone):
            return False, "شماره موبایل نامعتبر است. (مثال: 09123456789)"
            
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
