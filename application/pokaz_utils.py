from app import db
from models import Pokaz


def clear_exists_pkz(counter_id: int, month: int, year: int):
    pkzs = Pokaz.query.filter_by(counter=counter_id,
                                 p_month=month,
                                 p_year=year).all()
    try:
        for p in pkzs:
            db.session.delete(p)
        db.session.commit()
        return True
    except:
        return False
