import pandas as pd
from models.registrant import Registrant
from config.settings import BASE_DIR
import jdatetime

class ExportService:
    @staticmethod
    def export_to_excel(registrants_query, file_path=None):
        if not file_path:
            now_str = jdatetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = BASE_DIR / "exports"
            export_dir.mkdir(exist_ok=True)
            file_path = export_dir / f"export_{now_str}.xlsx"
            
        data = []
        for reg in registrants_query:
            data.append({
                "کد یکتا": str(reg.id),
                "نام و نام خانوادگی": reg.full_name,
                "شماره موبایل": reg.phone_number,
                "زمان ثبت‌نام": reg.registration_time,
                "شماره سانس": reg.session.session_number
            })
            
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return file_path
