from django import forms
from django.contrib.auth.models import User

from .models import Sala


class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['usuarios', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['usuarios'].queryset = User.objects.filter(email__contains='@inatec.edu.ni')
        self.fields['usuarios'].widget.attrs['class'] = 'form-select select-two'
        self.fields['usuarios'].required = False
