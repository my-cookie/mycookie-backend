from . import serializers
from .models import Message
from users.models import User
from rest_framework.views    import APIView
from rest_framework.response import Response
from rest_framework import exceptions, decorators, permissions, status
from datetime import datetime
from django.db import transaction
from django.core.cache import cache
#db저장과 동시에 성공여부를 반환한다. 성공일 시 프론트에서 websocket요청

class FlavorConfirm(APIView) :
    @transaction.atomic
    def post(self, request):
        user_id = 7
        copy_data = request.data.copy()
        if not 'flavor' in copy_data or not 'receiver' in copy_data:
            return Response(data={'error':'receiver and flavor are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        now = datetime.now().strftime('%Y-%m-%d')
        
        
        try:
            # today_msg = Message.objects.filter(created_at__contains = now)    #캐싱필요
            today_msgs = cache.get_or_set('today_msgs', Message.objects.filter(created_at__contains = now))
            count = today_msgs.filter(sender=user_id, receiver=copy_data['receiver']).count()
            if count == 3:
                return Response(data={'error':'no more message'}, status=status.HTTP_429_TOO_MANY_REQUESTS) 
        except:
            count = 0 

        try:
            receiver = User.objects.get(id=copy_data['receiver'])
            if receiver.is_active == False:
                return Response(data={'error':'this receiver is inactive'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
        except User.DoesNotExist:
            return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        copy_data['sender'] = user_id
        receiver_flavors = [myflavor.flavor_id for myflavor in receiver.myflavor.all()]  
        
        if copy_data['flavor'] in receiver_flavors:
            copy_data['is_success'] = True
            serializer = serializers.MessageSerializer(data=copy_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            receiver_uuid = receiver.uuid
            return Response(data={'msg_id':serializer.data['id'],'receiver_uuid': receiver_uuid,'is_success':True, 'remain': 2-count}, status=status.HTTP_201_CREATED)
            
        else:
            serializer = serializers.MessageSerializer(data=copy_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data={'is_success':False, 'remain': 2-count}, status=status.HTTP_201_CREATED)
        
        
class ReadMessage(APIView) :

    def post(self, request):
        try:
            if not 'msg_id' in request.data or not 'is_read' in request.data :
                return Response(data={'error':'msg_id and is_read are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            msg = Message.objects.get(id=request.data['msg_id'])
            serializer = serializers.ReadMessageSerializer(msg, request.data, partial = True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            sender = msg.sender
            sender_uuid = sender.uuid
            return Response(data={'success':'is_read was replaced with True', 'sender_uuid': sender_uuid}, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response(data={'error':'this message does not exist'}, status=status.HTTP_404_NOT_FOUND)
            