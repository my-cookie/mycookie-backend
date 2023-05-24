# app/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone
from users.models import SiteInfo
from django.core.cache import cache



class MessegeRoomConsumer(WebsocketConsumer):
    def connect(self):

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()  
        
        # current_connection = cache.get('websocket_list')
        # if current_connection is None:
        #     current_connection = [self.room_group_name]
        #     cache.set('websocket_list', current_connection, 60*60*24)
        # else:
        #     # if not self.room_group_name in current_connection:
        #     current_connection.append(self.room_group_name)
        #     cache.set('websocket_list', current_connection, 60*60*24)
        # try:
        #     now = timezone.now().strftime('%Y-%m-%d')
        #     latest_data = SiteInfo.objects.last()
        #     if latest_data.created_at.strftime('%Y-%m-%d') == now:
            
        #         latest_data.realtime_user = len(set(current_connection))
        #         latest_data.save()
        # except SiteInfo.DoesNotExist:
        #     pass          
      
        
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        
        try:
            current_connection = cache.get('websocket_list')
            current_connection = [room for room in current_connection if room != self.room_group_name]
            cache.set('websocket_list', current_connection, 60*60)
            
            
            try:
                now = timezone.now().strftime('%Y-%m-%d')
                latest_data = SiteInfo.objects.last()
                if latest_data.created_at.strftime('%Y-%m-%d') == now:
                
                    latest_data.realtime_user = len(set(current_connection))
                    latest_data.save()
            except SiteInfo.DoesNotExist:
                pass
        except:
            pass
        

    def receive(self, text_data):
        # Receive message from WebSocket
        # try:
        #     current_connection = cache.get('websocket_list')
        #     current_connection.remove(self.room_group_name)
        #     cache.set('websocket_list', current_connection, 60*60*24)
            
        #     try:
        #         now = timezone.now().strftime('%Y-%m-%d')
        #         latest_data = SiteInfo.objects.last()
        #         if latest_data.created_at.strftime('%Y-%m-%d') == now:
                
        #             latest_data.realtime_user = len(set(current_connection))
        #             latest_data.save()
        #     except SiteInfo.DoesNotExist:
        #         pass
        # except:
        #     pass
        text_data_json = json.loads(text_data)
        # 메시지 읽음 처리: 받은 사람이 메시지를 클릭하면 post & websocket(sender_uuid) 연결
        if 'is_read' in text_data_json:
            
            msg_id = text_data_json['msg_id']
            is_read = text_data_json['is_read']

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_id': msg_id,
                    'is_read': is_read
                }
            )
        
        # 메시지 발송 처리
        else:
            msg_id = text_data_json['msg_id']

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'msg_id': msg_id,
                }
            )
        
        #프론트에서 메시지 보낼 때 보낸 즉시 roomname을 수신자에서 발신자의 것으로 바꾸어야한다.

    def chat_message(self, event):    #in comming messate의 "type" 과 동일한 함수 이름
        # Receive message from room group
        # try:
        #     current_connection = cache.get('websocket_list')
        #     current_connection.remove(self.room_group_name)
        #     cache.set('websocket_list', current_connection, 60*60*24)
    
        #     try:
        #         now = timezone.now().strftime('%Y-%m-%d')
        #         latest_data = SiteInfo.objects.last()
        #         if latest_data.created_at.strftime('%Y-%m-%d') == now:
                
        #             latest_data.realtime_user = len(set(current_connection))
        #             latest_data.save()
        #     except SiteInfo.DoesNotExist:
        #         pass
        # except:
        #     pass
        # 메시지 읽음 처리: 프론트에서 해당 메시지 번호에 대한 디스플레이를 읽음으로 바꾼다
        if 'is_read' in event:
            msg_id = event['msg_id']
            is_read = event['is_read']
            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'msg_id': msg_id,
                'is_read': is_read
            }))
            
        # 메시지 도착 알림
        else:
            msg_id = event['msg_id']
            # Send message to WebSocket
            self.send(text_data=json.dumps({
                'msg_id': msg_id,
            }))
        
   