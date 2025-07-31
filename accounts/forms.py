from django import forms
from baseSQL.models import Utilisateur
class LoginForm(forms.Form):
    user = forms.CharField(label="username")
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

class CaissierCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")


    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'contact','adresse', 'password']

def save(self, commit= True):
    user = super().save(commit=False)
    user.set_password(self.cleaned_data['password'])### hash du mot de passe
    user.role= 'caissier'
    user.is_active = True  # Activation de l'utilisateur
    if commit:
        user.save()
    return user            



#####Formulairede modifciation caissier

class CaissierForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'contact','first_name', 'last_name','email',  'adresse']


### Modificationdes informations users
# from django import forms
from baseSQL.models import Utilisateur

class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name', 'last_name', 'email', 'contact', 'adresse', 'photo']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }

class PhotoProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['photo']  #         


class InfosProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['first_name','last_name', 'email', 'contact', 'adresse']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
        }
