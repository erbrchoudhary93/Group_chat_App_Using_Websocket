from channels.consumer import SyncConsumer,AsyncConsumer,StopConsumer
from time import sleep
import asyncio
import json
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async

from .models import Group,Chat

# Dynamic group name
class MySyncConsumer(SyncConsumer):
    
    """  This handelar is called when client initially opens a connection and is about to finish the websocket handshake """
    def websocket_connect(self,event):
        # print('websocket connected...',event)
        # print('channel layer...',self.channel_layer)  # get default channel layer from a project
        # print('channel Name...',self.channel_name)  # get channel name
        # get group name
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        # print("Group Name .......",self.group_name)
        async_to_sync(self.channel_layer.group_add)(self.group_name,self.channel_name)
        self.send({
            'type':'websocket.accept'
        })
        
    def websocket_receive(self,event):
        
        # print('websocket received from client....',event['text'])
        # print('Type of websocket received from client....',type(event['text']))
        data = json.loads(event['text'])
        print(self.scope['user'])
        #find group object
        group = Group.objects.get(name=self.group_name)
        if self.scope['user'].is_authenticated:
        
            # create chat object
            chat= Chat(
                content=data['msg'].strip(),
                group =group
                )
            chat.save()
            data['user'] = self.scope['user'].username
            async_to_sync (self.channel_layer.group_send)(
                self.group_name,
                {
                    'type':'chat.message',
                    'message':json.dumps(data)
                })
            
        else:
            self.send({
                'type':'websocket.send',
                'text':json.dumps({"msg":"Login Requird","user":"guest"})
                })
        
    def chat_message(self,event):
        # print('Event ... ',event)
        # print('Actual Data ... ',event['message'])
        # print(' Type of Actual Data ... ',type(event['message']))
        self.send({
            'type':'websocket.send',
            'text':event['message']
            })
        
        
        
        
    def websocket_disconnect(self,event):
        # print('websocket Diconnectd....',event)
        # print('channel Layer ...',self.channel_layer)
        # print('channel Layer ...',self.channel_name)
        async_to_sync (self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()
       
    
    
    
# Async Consumer
class MyAsyncConsumer(AsyncConsumer):
    
    """  This handelar is called when client initially opens a connection and is about to finish the websocket handshake """
    async def websocket_connect(self,event):
        # print('websocket connected...',event)
        # print('channel layer...',self.channel_layer)  # get default channel layer from a project
        # print('channel Name...',self.channel_name)  # get channel name
        # get group name
       
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        # print("Group Name .......",self.group_name)
        await self.channel_layer.group_add(
            self.group_name,self.channel_name)
        await self.send({
            'type':'websocket.accept'
        })
        
    async def websocket_receive(self,event):
        
        # print('websocket received from client....',event['text'])
        # print('Type of websocket received from client....',type(event['text']))
        data = json.loads(event['text'])
        #find group object
        group = await database_sync_to_async (Group.objects.get)(name=self.group_name)
        if self.scope['user'].is_authenticated:
        
        # create chat object
            chat= Chat(
                content=data['msg'].strip(),
                group =group
                )
            await database_sync_to_async(chat.save)()
            data['user'] = self.scope['user'].username
    
        
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type':'chat.message',
                    'message':json.dumps(data)
                })
            
        else:
            await self.send({
                'type':'websocket.send',
                'text':json.dumps({"msg":"Login Requird","user":"guest"})
                })
        
    async def chat_message(self,event):
        # print('Event ... ',event)
        # print('Actual Data ... ',event['message'])
        # print(' Type of Actual Data ... ',type(event['message']))
        await self.send({
            'type':'websocket.send',
            'text':event['message']
            })
        
        
        
        
    async def websocket_disconnect(self,event):
        # print('websocket Diconnectd....',event)
        # print('channel Layer ...',self.channel_layer)
        # print('channel Layer ...',self.channel_name)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()