# app/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
# from .models import Message

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
        
    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # Receive message from WebSocket
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
        
   