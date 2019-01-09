from django.urls import path
from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views
from .forms import MyLoginForm

urlpatterns = [
    path('', views.extendsView.as_view(), name ='index'),
    #path('', views.LoginIndex.as_view(), name ='index'),
    #path('extends', views.extends, name= 'extends'),
    path('extends/', views.extendsView.as_view(), name='extends'),
    path('extends/ansibledemo/', views.AnsibleDemo.as_view(), name='ansibledemo'),
    path('extends/rulesdemo/', views.RulesDemo.as_view(), name='rulesdemo'),
    path('extends/createhost/', views.CreateHostView.as_view(), name='createhost'),
    path('extends/createnetwork/', views.CreateNetworkView.as_view(), name='createnetwork'),
    path('accounts/login/', auth_views.LoginView.as_view(form_class=MyLoginForm), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout')
    #path('accounts/', include('django.contrib.auth.urls'), name='loginpage')
]