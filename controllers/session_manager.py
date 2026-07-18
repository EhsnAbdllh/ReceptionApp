import jdatetime
from models.session import Session
from models.registrant import Registrant

class SessionManager:
    @staticmethod
    def _parse_time(time_str):
        return jdatetime.datetime.strptime(time_str, "%Y/%m/%d %H:%M")

    @staticmethod
    def is_overlap(start_time_str, end_time_str, exclude_session_id=None):
        new_start = SessionManager._parse_time(start_time_str)
        new_end = SessionManager._parse_time(end_time_str)
        
        if new_start >= new_end:
            return True # Invalid time range

        sessions = Session.select()
        for session in sessions:
            if exclude_session_id and session.id == exclude_session_id:
                continue
            
            s_start = SessionManager._parse_time(session.start_time)
            s_end = SessionManager._parse_time(session.end_time)
            # Overlap condition: max(start1, start2) < min(end1, end2)
            if max(new_start, s_start) < min(new_end, s_end):
                return True
        return False

    @staticmethod
    def get_current_session():
        now = jdatetime.datetime.now()
        sessions = Session.select()
        for session in sessions:
            s_start = SessionManager._parse_time(session.start_time)
            s_end = SessionManager._parse_time(session.end_time)
            if s_start <= now <= s_end:
                return session
        return None

    @staticmethod
    def get_remaining_capacity(session):
        registered_count = session.registrants.count()
        return session.total_capacity - registered_count

    @staticmethod
    def get_next_session_number():
        # Get the max session number
        max_session = Session.select().order_by(Session.session_number.desc()).first()
        if max_session:
            return max_session.session_number + 1
        return 1

    @staticmethod
    def delete_session(session_id):
        # Explicit cascade delete for safety
        Registrant.delete().where(Registrant.session == session_id).execute()
        Session.delete().where(Session.id == session_id).execute()
