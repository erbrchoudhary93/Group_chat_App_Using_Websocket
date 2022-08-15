from django.urls import path
from .import views



urlpatterns = [
    path('',views.index,name='index'),
    path('group/<str:groupname>',views.index_group,name='group'),
    # path('',views.index_group,name='index')
]