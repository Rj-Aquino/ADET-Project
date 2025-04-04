from django import forms

class SearchForm(forms.Form):
    title = forms.CharField(max_length=200, label='Title')
    abstract = forms.CharField(widget=forms.Textarea, label='Abstract')
