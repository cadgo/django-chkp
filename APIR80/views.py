from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models, forms

class LoginIndex(generic.ListView, LoginRequiredMixin):
    model = models.R80Users
    template_name = 'APIR80/index.html'


# Create your views here.
def index2(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return render(request, 'APIR80/extend.html')
    return render(request, 'APIR80/index.html')

def extends(request):
    if request.user.is_authenticated:
        return render(request, 'APIR80/extend.html')
    else:
        return render(request, 'APIR80/index.html')


class AnsibleDemo2(LoginRequiredMixin, generic.ListView):
      template_name = 'APIR80/ansibledemo.html'
      login_url = '../../r80api/accounts/login/'
      model = models.MGMTServer
      form_class = forms.AnsibleSMSDeploy
      success_url = '/thanks/'
      redirect_field_name = 'redirect_to'

      def form_valid(self, form):
          return super().form_valid(form)

class AnsibleDemo(LoginRequiredMixin, View):
    template_name = 'APIR80/ansibledemo.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.AnsibleSMSDeploy
    redirect_field_name = 'redirect_to'

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        formGW = forms.AnsibleFWDeploy()
        return render(request, self.template_name, {'form1': form, 'formGWt': formGW})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            print(request.POST)
            SmartCenterName = form.cleaned_data['SmartCenterName']
            IPAddress = form.cleaned_data['SubNetIPAddress']
            print(SmartCenterName + ' ' + IPAddress)
            return HttpResponse('/suscess/')
        return render(request, self.template_name, {'form': form})


# class AnsibleDemo(View):
#     from_class = forms.AnsibleFirewallDeploy

class extendsView(LoginRequiredMixin, generic.ListView):
    template_name = 'APIR80/extend.html'
    login_url = '../../r80api/accounts/login/'
    model = models.MGMTServer
    redirect_field_name = 'redirect_to'