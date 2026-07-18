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
    def register(full_name, phone_number, session):
        if not session:
            return False, "سانس فعالی یافت نشد."
        
        if not RegistrationManager.validate_name(full_name):
            return False, "نام وارد شده نامعتبر است."

        if not RegistrationManager.validate_phone(phone_number):
            return False, "شماره موبایل نامعتبر است. (مثال: 09123456789)"

        remaining = SessionManager.get_remaining_capacity(session)
        if remaining <= 0:
            return False, "ظرفیت سانس پر شده است."
            
        now_str = jdatetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        try:
            reg = Registrant.create(
                full_name=full_name,
                phone_number=phone_number,
                registration_time=now_str,
                session=session
            )
            try:
                PrinterService.print_label(reg)
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
