from django.shortcuts import render
from django.http import HttpResponse
from django.views import generic, View
from django.contrib.auth.mixins import LoginRequiredMixin
from . import models, forms
from . import tasks
from django.core.exceptions import SuspiciousOperation

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

class RulesDemo(LoginRequiredMixin, View):
    template_name = 'APIR80/rulesdemo.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.RuleBasesForm
    redirect_field_name = 'redirect_to'
    RulesDemoForms = {}

    def __init__(self):
        self.RulesDemoForms['rulesform'] = self.form_class()
        self.RulesDemoForms['R80UsersForm'] = forms.ModelsUsersAndMgmtServer()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.RulesDemoForms)


class AnsibleDemo(LoginRequiredMixin, View):
    template_name = 'APIR80/ansibledemo.html'
    login_url = '../../r80api/accounts/login/'
    form_class = forms.AnsibleSMSDeploy
    redirect_field_name = 'redirect_to'
    AnsibleForms = {}

    def __init__(self):
        self.AnsibleForms["formsms"] = self.form_class()
        self.AnsibleForms["formGWt"] = forms.AnsibleFWDeploy()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.AnsibleForms)

    def post(self, request, *args, **kwargs):
        if request.POST.get('FwDeployFormHidden') == 'True':
            #INTEGRAR VALIDACIONES DE REGEX PARA LAS IPS SI SE 1.1.1.1. LO TOMA COMO VALIDO
            print("DeployGW")
            form = forms.AnsibleFWDeploy(request.POST)
            if form.is_valid():
                print("Form Fw is OK")
                tasks.counttomil()
            else:
                SuspiciousOperation("Invalid request: no able to process the form")
        if request.POST.get('SMSDeployFormHidden') == 'True':
            print("DeploySMS")
            form = self.form_class(request.POST)
            if form.is_valid():
                print("Form SMSDeploy OK")
            else:
                SuspiciousOperation("Invalid request: no able to process the form")
        # form = self.form_class(request.POST)
        # print(request.POST)
        # if form.is_valid():
        #     print(request.POST)
        #     SmartCenterName = form.cleaned_data['SmartCenterName']
        #     IPAddress = form.cleaned_data['SubNetIPAddress']
        #     print(SmartCenterName + ' ' + IPAddress)
        #     return HttpResponse('/suscess/')
        return render(request, self.template_name, self.AnsibleForms)

# class AnsibleDemo(View):
#     from_class = forms.AnsibleFirewallDeploy

class extendsView(LoginRequiredMixin, generic.ListView):
    template_name = 'APIR80/extend.html'
    login_url = '../../r80api/accounts/login/'
    model = models.MGMTServer
    redirect_field_name = 'redirect_to'