# **Chat App Using Websocket**

## configuration in settings.py file

```python
# app install
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
]
#asgi configurationn
ASGI_APPLICATION = 'websocket__layers.asgi.application'

# database configuration

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'websocket__layers',
        'USER':'postgres',
        'PASSWORD': 'root',
        'HOST':'localhost',
        'PORT':'5432'
    }
}

#redis configuration

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}


```
## configuration in asgi.py file

```python
import os
from channels.routing import ProtocolTypeRouter,URLRouter
from django.core.asgi import get_asgi_application
import app.routing
from channels.auth import AuthMiddlewareStack

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'websocket__layers.settings')
application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket':AuthMiddlewareStack(URLRouter(
        
        app.routing.websocket_urlpattern
        )
    )
    })

```

## configuration in urls.py file
```python
from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('app.urls'))
]
```

## configuration in app/views.py file
```python
from django.shortcuts import render
from .models import Group,Chat

# Create your views here.

def index(request):
    return render(request,'app/index.html')


def index_group(request,groupname):
    print("Group Name : ",groupname)
    group= Group.objects.filter(name=groupname).first()
    chats=[]
    if group:
        chats = Chat.objects.filter(group=group)
        
    else:
        group = Group(name=groupname)
        group.save()
    return render(request,'app/index_group.html',{'group':groupname,'chats':chats})

```

## configuration in app/urls.py file

```python
from django.urls import path
from .import views
urlpatterns = [
    path('',views.index,name='index'),
    path('group/<str:groupname>',views.index_group,name='group'),
]
```

## configuration in app/conumers.py file

```python
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
       
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        # print("Group Name .......",self.group_name)
        async_to_sync(self.channel_layer.group_add)(self.group_name,self.channel_name)
        self.send({
            'type':'websocket.accept'
        })
        
    def websocket_receive(self,event):
        
        
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
        
        self.send({
            'type':'websocket.send',
            'text':event['message']
            })
        
        
        
        
    def websocket_disconnect(self,event):
        
        async_to_sync (self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()
       
    
    
    
# Async Consumer
class MyAsyncConsumer(AsyncConsumer):
    
    """  This handelar is called when client initially opens a connection and is about to finish the websocket handshake """
    async def websocket_connect(self,event):
       
        # get group name
       
        self.group_name = self.scope['url_route']['kwargs']['groupkaname']
        # print("Group Name .......",self.group_name)
        await self.channel_layer.group_add(
            self.group_name,self.channel_name)
        await self.send({
            'type':'websocket.accept'
        })
        
    async def websocket_receive(self,event):
        
        
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
        
        await self.send({
            'type':'websocket.send',
            'text':event['message']
            })
        
        
        
        
    async def websocket_disconnect(self,event):
        
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        raise StopConsumer()

```

## configuration in app/routing.py file
```python
from django.urls import path
from .import consumers
websocket_urlpattern  =  [ 
        
        path('ws/sc/<str:groupkaname>/',consumers.MySyncConsumer.as_asgi()),                  
        path('ws/asc/<str:groupkaname>/',consumers.MyAsyncConsumer.as_asgi()),                  
        path('ws/sc/',consumers.MySyncConsumer.as_asgi()),                  
        path('ws/asc/',consumers.MyAsyncConsumer.as_asgi()),                  
                          
]
```
## configuration in app/templates/app/index_group.html.py file
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat app</title>
</head>
<body>
    

<h1>Websocket Testing</h1>

<h1>Group Name :{{group}}</h1>




<textarea name="" id="chat-log" cols="100" rows="20">
    
    {% for chat in chats %}

    {{chat.content}}
        
    {% endfor %}
        
</textarea><br>

<h4>Type Your Message</h4>
<input type="text" id="chat-message-input" size="100"><br>
<input type="button" value="Send" id="chat-message-submit">

<a href="{% url 'index' %}">Back To Chatting Room</a>

{{group|json_script:"group-name"}}




    <script>
        // var ws = new WebSocket('ws://127.0.0.1:8000/ws/sc/')
        // var was = new WebSocket('ws://127.0.0.1:8000/ws/asc/')


        const groupName = JSON.parse(document.getElementById('group-name').textContent)
        console.log(groupName)
         // var was = new WebSocket('ws://127.0.0.1:8000/ws/asc/')

         var ws = new WebSocket(
               
            'ws://'
            +window.location.host 
            +'/ws/asc/'+ groupName 
            +'/'

         )



        // Sync  function



        ws.onopen=function(){
            console.log('Websocket connection Open....')
            // ws.send('Hi from client')
        }
        ws.onmessage=function(event){
            console.log('Message Received from server....',event.data)
            console.log(typeof(event.data))
            const data = JSON.parse(event.data)
            console.log(data.msg)
            console.log(data.user)
            console.log(typeof(data))
            document.querySelector('#chat-log').value+=(data.user+" : "+ data.msg+"\n")

        }
        ws.onclose=function(){
            console.log('Websocket connection closed....');
        };
        document.getElementById('chat-message-submit').onclick =
            function(event){
                const messageInputDom = document.getElementById('chat-message-input')
                const message = messageInputDom.value
                ws.send(JSON.stringify({
                    'msg':message
                }))
                messageInputDom.value = ''
            }


        
    </script>
</body>
</html>



```



