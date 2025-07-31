from django import forms
from baseSQL.models import Client , Fournisseur



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom_client', 'contact', 'email', 'adresse', 'point']
        widgets = {
            'nom_client': forms.TextInput(attrs={'class': 'form-control'}),
            'contact' : forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'point': forms.NumberInput(attrs={'class': 'form-control'}),

        }

class FrsForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom_frs', 'contact', 'email', 'adresse', 'pays', 'type_frs']
        widgets = {
            'nom_frs': forms.TextInput(attrs={'class': 'form-control'}),
            'contact' : forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'pays': forms.TextInput(attrs={'class': 'form-control'}),
            'type_frs':forms.TextInput(attrs={'class': 'form-control'}),

        }                                                