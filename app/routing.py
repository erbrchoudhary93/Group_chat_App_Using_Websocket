from django.urls import path
from .import consumers




websocket_urlpattern  =  [ 
        
        path('ws/sc/<str:groupkaname>/',consumers.MySyncConsumer.as_asgi()),                  
        path('ws/asc/<str:groupkaname>/',consumers.MyAsyncConsumer.as_asgi()),                  
        path('ws/sc/',consumers.MySyncConsumer.as_asgi()),                  
        path('ws/asc/',consumers.MyAsyncConsumer.as_asgi()),                  
                          
]