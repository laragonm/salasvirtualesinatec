from django import forms
from django.contrib.auth.models import User


class UsuarioForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['groups', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].widget.attrs['class'] = 'form-select select-two'
