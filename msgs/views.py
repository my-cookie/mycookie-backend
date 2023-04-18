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

@decorators.permission_classes([permissions.IsAuthenticated])
class SendMsgView(APIView) :
    @transaction.atomic
    def post(self, request):
        user_id = request.user.id
        # user_id = 7
        copy_data = request.data.copy()
        if not 'flavor' in copy_data or not 'receiver' in copy_data:
            return Response(data={'error':'receiver and flavor are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            receiver = User.objects.get(id=copy_data['receiver'])
            if receiver.is_active == False:
                return Response(data={'error':'this receiver is inactive'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except User.DoesNotExist:
            return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        now = datetime.now().strftime('%Y-%m-%d')
        
        count = cache.get(f'count_{user_id}_{copy_data["receiver"]}_{now}')
        if count is None:
            today_msgs = Message.objects.filter(created_at__contains = now)
            count = today_msgs.filter(sender=user_id, receiver=copy_data['receiver']).count()
            cache.set(f'count_{user_id}_{copy_data["receiver"]}_{now}', count, 60*60*24)

        if count == 3:
            return Response(data={'error':'no more message'}, status=status.HTTP_429_TOO_MANY_REQUESTS) 
               
                
        copy_data['sender'] = user_id
        
        receiver_flavors = cache.get(f'flavors_{copy_data["receiver"]}')
        
        if receiver_flavors is None:
            receiver_flavors = [myflavor.flavor_id for myflavor in receiver.myflavor.all()]  
            cache.set(f'flavors_{copy_data["receiver"]}', receiver_flavors, 60*60*24*7*5)
        
        if copy_data['flavor'] in receiver_flavors:
            copy_data['is_success'] = True
            serializer = serializers.MessageSerializer(data=copy_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            msgs = cache.get(f'sender_msg_{user_id}')
            if msgs is None:
                msgs = Message.objects.filter(sender = user_id, is_success = True, sender_deleted = False, sender_canceled = False)
                msgs_serializer = serializers.SenderMsgSerializer(msgs, many=True)
                msgs = msgs_serializer.data
                
            new_msg = Message.objects.get(id = serializer.data["id"])
            new_msg_serializer = serializers.SenderMsgSerializer(new_msg)
            msgs = msgs.insert(0, new_msg_serializer.data)
            cache.set(f'sender_msg_{user_id}', msgs, 60*60*24)
            
            receiver_id = copy_data['receiver']   
             
            msgs = cache.get(f'receiver_msg_{receiver_id}')
            if msgs is None:
                msgs = Message.objects.filter(receiver = receiver_id, is_success = True, receiver_deleted = False, sender_canceled = False)
                msgs_serializer = serializers.ReceiverMsgSerializer(msgs, many=True)
                msgs = msgs_serializer.data
                
            new_msg_serializer = serializers.ReceiverMsgSerializer(new_msg)
            msgs = msgs.insert(0, new_msg_serializer.data)
            cache.set(f'receiver_msg_{receiver_id}', msgs, 60*60*24)
            cache.set(f'count_{user_id}_{copy_data["receiver"]}_{now}', count+1, 60*60*24)
                
            return Response(data={'msg_id' : serializer.data['id'], "receiver_nickname":receiver.nickname,"is_success" : serializer.data["is_success"], 'receiver_uuid': receiver.uuid, 'remain': 2-count}, status=status.HTTP_201_CREATED)
            
        else:
            serializer = serializers.MessageSerializer(data=copy_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            cache.set(f'count_{user_id}_{copy_data["receiver"]}_{now}', count+1, 60*60*24)
            return Response(data={"receiver_nickname":receiver.nickname,"receiver":serializer.data['receiver'], "content": serializer.data['content'], "is_anonymous": serializer.data['is_anonymous'],"is_success" : False, 'remain': 2-count}, status=status.HTTP_201_CREATED)

            
@decorators.permission_classes([permissions.IsAuthenticated])            
class ReadMessageView(APIView) :

    def post(self, request):
        try:
            user_id = request.user.id
            # user_id = 8
            
            if not 'message_id' in request.data:
                return Response(data={'error':'message_id is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                msg = Message.objects.get(id=request.data['message_id'])
                sender_id = msg.sender_id
                msg.is_read = True
                msg.save()                
                
                msgs = cache.get(f'sender_msg_{user_id}')
                if msgs is None:
                    pass
                else:
                    temp = []
                    for msg in msgs:
                        if msg['id'] == request.data['message_id']:
                            msg['is_read'] = True
                            temp.append(msg)
                        else:
                            temp.append(msg) 
                    cache.set(f'sender_msg_{user_id}', temp, 60*60*24)
                    
                msgs = cache.get(f'receiver_msg_{user_id}')
                
                if msgs is None:
                    pass
                else:
                    temp = []
                    for msg in msgs:
                        if msg['id'] == request.data['message_id']:
                            msg['is_read'] = True
                            temp.append(msg)
                        else:
                            temp.append(msg) 
                    cache.set(f'receiver_msg_{user_id}', temp, 60*60*24)
                    
                
                try:
                    sender_uuid = User.objects.get(id=sender_id).uuid
                    
                except User.DoesNotExist:
                    return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)
                
                return Response(data={'success':'is_read was replaced with True', 'sender_uuid': sender_uuid}, status=status.HTTP_200_OK)
        
        except Message.DoesNotExist:
            return Response(data={'error':'this message does not exist'}, status=status.HTTP_404_NOT_FOUND)


@decorators.permission_classes([permissions.IsAuthenticated])
class RemainMsgView(APIView) :

    def post(self, request): 
        if not 'receiver' in request.data:
            return Response(data={'error':'receiver is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            receiver = User.objects.get(id=request.data['receiver'])
           
            if receiver.is_active == False:
                return Response(data={'error':'this receiver is inactive'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except User.DoesNotExist:
            return Response(data={'error':'this user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        user_id = request.user.id
        user = User.objects.get(id = user_id)
        # user_id = 7
        now = datetime.now().strftime('%Y-%m-%d')
        count = cache.get(f'count_{user_id}_{request.data["receiver"]}_{now}')
        if count is None:
            today_msgs = Message.objects.filter(created_at__contains = now)    
            count = today_msgs.filter(sender=user_id, receiver=request.data['receiver']).count()
            cache.set(f'count_{user_id}_{receiver.id}_{now}', count, 60*60*24)
            
        return Response(data={'sender_nickname': user.nickname,'receiver_nickname':receiver.nickname,'count':3-count}, status=status.HTTP_200_OK)


@decorators.permission_classes([permissions.IsAuthenticated])
class SenderMsgView(APIView) :
    
    def get(self, request):
        # user_id = 10
        user_id = request.user.id
        msgs = cache.get(f'sender_msg_{user_id}')
        if msgs is None:
            msgs = Message.objects.filter(sender = user_id, is_success = True, sender_deleted = False, sender_canceled = False)
            serializer = serializers.SenderMsgSerializer(msgs, many=True)
            msgs = serializer.data
            cache.set(f'sender_msg_{user_id}', msgs, 60*60*24)
            
        return Response(data=msgs, status=status.HTTP_200_OK)
    
@decorators.permission_classes([permissions.IsAuthenticated])
class ReceiverMsgView(APIView) :
    
    def get(self, request):
        # user_id = 8
        user_id = request.user.id
        msgs = cache.get(f'receiver_msg_{user_id}')
        if msgs is None:
            msgs = Message.objects.filter(receiver = user_id, is_success = True, receiver_deleted = False, sender_canceled = False)
            msgs_serializer = serializers.ReceiverMsgSerializer(msgs, many=True)
            msgs = msgs_serializer.data
            cache.set(f'receiver_msg_{user_id}', msgs, 60*60*24)
            
        return Response(data=msgs, status=status.HTTP_200_OK)
        
@decorators.permission_classes([permissions.IsAuthenticated])    
class SpamReportView(APIView) :
    
    def post(self, request):
        try:
            user_id = request.user.id
            # user_id = 8
            if not "message" in request.data:
                return Response(data={'error':'message is required'}, status=status.HTTP_400_BAD_REQUEST)
            msgs = Message.objects.get(id = request.data["message"])
            if msgs.is_spam == True:
                return Response(data={'message':'this message is aleady reported as spam'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                
            
            with transaction.atomic():
                
                copy_data = request.data.copy()
                copy_data['is_spam'] = True
                serializer = serializers.SpamMessageSerializer(msgs, copy_data, partial = True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                serializer = serializers.SpamSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()        
                
                msgs = cache.get(f'receiver_msg_{user_id}')
                if msgs is None:
                    pass
                else:
                    temp = []
                    for msg in msgs:
                        if msg['id'] == request.data['message']:
                            msg['is_spam'] = True
                            temp.append(msg)
                        else:
                            temp.append(msg) 
                    cache.set(f'receiver_msg_{user_id}', temp, 60*60*24)
            
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        except Message.DoesNotExist:
            return Response(data={'error':'this message does not exist'}, status=status.HTTP_404_NOT_FOUND)


@decorators.permission_classes([permissions.IsAuthenticated])
class ReceiverDeleteMsgView(APIView) :
    
    def patch(self, request):
        # user_id = 8
        user_id = request.user.id
        if not "message_id" in request.data:
            return Response(data={'error':'message_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():     
            msg = Message.objects.get(id = request.data['message_id'])
            msg.receiver_deleted = True
            msg.save()
            
            msgs = cache.get(f'receiver_msg_{user_id}')
                
            if msgs is None:
                pass
            else:
                msgs = [msg for msg in msgs if msg['id'] != request.data['message_id']]
                cache.set(f'receiver_msg_{user_id}', msgs, 60*60*24)
            return Response(status=status.HTTP_200_OK)


@decorators.permission_classes([permissions.IsAuthenticated])
class SenderDeleteMsgView(APIView) :
    
    def patch(self, request):
        # user_id = 7
        user_id = request.user.id
        if not "message_id" in request.data:
            return Response(data={'error':'message_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():    
            msg = Message.objects.get(id = request.data['message_id'])
            msg.sender_deleted = True
            msg.save()
            
            msgs = cache.get(f'sender_msg_{user_id}')
            
            if msgs is None:
                pass
            else:
                msgs = [msg for msg in msgs if msg['id'] != request.data['message_id']]
                cache.set(f'sender_msg_{user_id}', msgs, 60*60*24)
                
            return Response(status=status.HTTP_200_OK)


@decorators.permission_classes([permissions.IsAuthenticated])
class SenderCancelMsgView(APIView) :
    
    def patch(self, request):
        # user_id = 7
        user_id = request.user.id
        try:
            if not "message_id" in request.data:
                return Response(data={'error':'message_id is required'}, status=status.HTTP_400_BAD_REQUEST)
                
            msg = Message.objects.get(id = request.data['message_id'])
            receiver_id = msg.receiver_id
            
            if msg.is_read == True :
                return Response(data={'error':'message is already read'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            msg.sender_canceled = True
            msg.save()
            
            with transaction.atomic():
                msgs = cache.get(f'sender_msg_{user_id}')
            
                if msgs is None:
                    pass
                else:
                    msgs = [msg for msg in msgs if msg['id'] != request.data['message_id']]
                    cache.set(f'sender_msg_{user_id}', msgs, 60*60*24)
            
                msgs = cache.get(f'receiver_msg_{receiver_id}')
                
                if msgs is None:
                    pass
                else:
                    msgs = [msg for msg in msgs if msg['id'] != request.data['message_id']]
                    cache.set(f'receiver_msg_{receiver_id}', msgs, 60*60*24)   
                
                return Response(status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response(data={'error':'this message is does not exist'}, status=status.HTTP_404_NOT_FOUND)
         