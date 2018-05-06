from django import forms


class SearchUserForm(forms.Form):
    username = forms.CharField(max_length=150)
