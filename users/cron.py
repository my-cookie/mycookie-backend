from .models import TemporalNickname
from datetime import datetime

def delete_temp_nickname():
    
    TemporalNickname.objects.all().delete()
    print(f"{datetime.now()}:temporal nickname deleted !")
    