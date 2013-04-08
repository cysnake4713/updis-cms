#encoding:utf-8
from openerplib import AuthenticationError

__author__ = 'Zhou Guangwen'
from django import forms

class CommentForm(forms.Form):
    body = forms.CharField(max_length=200,widget=forms.Textarea)
    is_anonymous = forms.BooleanField(required=False,initial=False)
    attachment = forms.FileField(required=False)
class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(max_length=60, widget=forms.PasswordInput)

    def __init__(self,*args,**kwargs):
        self.request = kwargs.pop('request', None)
        super(LoginForm,self).__init__(*args,**kwargs)
    def clean(self):
        erpsession = self.request.erpsession
        old_login = erpsession.login
        old_password = erpsession.password
        try:
            erpsession.login = self.cleaned_data['login']
            erpsession.password = self.cleaned_data['password']
            erpsession.check_login()
            return self.cleaned_data
        except AuthenticationError,e:
            erpsession.login = old_login
            erpsession.password = old_password
            raise forms.ValidationError(u"登录失败")


class SearchForm(forms.Form):
    search_context = forms.CharField(max_length=200,widget=forms.TextInput)