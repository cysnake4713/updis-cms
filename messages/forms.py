__author__ = 'Zhou Guangwen'
from django import forms

class CommentForm(forms.Form):
    body = forms.CharField(max_length=200,widget=forms.Textarea)
    is_anonymous = forms.BooleanField(required=False,initial=False)
    attachment = forms.FileField(required=False)
