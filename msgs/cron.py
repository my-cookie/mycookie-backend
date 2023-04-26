from .models import Message
from datetime import date, datetime
 


def delete_failed_massage():
   
    today = date.today()
    print(today)
    today = today.strftime('%Y-%m-%d')
    Message.objects.filter(created_at__lt = today, is_success = False).delete()
    print(f"{datetime.now()}:failed message deleted !")
    