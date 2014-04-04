#encoding:utf-8
from django.forms.models import ModelForm
from messages.models import BirthdayWishModel
from openerplib import AuthenticationError

__author__ = 'Zhou Guangwen'
from django import forms


class CommentForm(forms.Form):
    body = forms.CharField(max_length=5000, widget=forms.Textarea)
    is_anonymous = forms.BooleanField(required=False, initial=False)
    attachment = forms.FileField(required=False)


class LoginForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(max_length=60, widget=forms.PasswordInput)


class SearchForm(forms.Form):
    search_context = forms.CharField(max_length=200, widget=forms.TextInput)


class BirthDayForm(ModelForm):
    body = forms.CharField()
    no_wish = forms.CharField()

    class Meta:
        model = BirthdayWishModel
        exclude = ('page', 'position', 'placeholder', 'language', 'plugin_type')