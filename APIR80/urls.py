from django.urls import path
from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.LoginIndex.as_view(), name ='index'),
    #path('extends', views.extends, name= 'extends'),
    path('extends/', views.extendsView.as_view(), name='extends'),
    path('extends/ansibledemo/', views.AnsibleDemo.as_view(), name='ansibledemo'),
    path('accounts/', include('django.contrib.auth.urls'), name='loginpage')
]