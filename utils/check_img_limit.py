from datetime import datetime, date, time
from models.image_model import Image

def check_daily_limit(db, user_id, limit=1):
    today = date.today()

    start_of_day = datetime.combine(today, time.min)
    end_of_day = datetime.combine(today, time.max)

    count = db.query(Image).filter(
        Image.user_id == user_id,
        Image.created_at >= start_of_day,
        Image.created_at <= end_of_day
    ).count()
    print('count',count)

    return count >= limit