#encoding:utf-8
from openerplib import AuthenticationError

__author__ = 'Zhou Guangwen'
from django import forms


class CommentForm(forms.Form):
    body = forms.CharField(max_length=200, widget=forms.Textarea)
    is_anonymous = forms.BooleanField(required=False, initial=False)
    attachment = forms.FileField(required=False)


class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(max_length=60, widget=forms.PasswordInput)


class SearchForm(forms.Form):
    search_context = forms.CharField(max_length=200, widget=forms.TextInput)