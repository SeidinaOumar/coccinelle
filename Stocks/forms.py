from django import forms
from baseSQL.models import Produit, Fournisseur , CategorieProduit


class ApprovisionnementForm(forms.Form):
    produit = forms.ModelChoiceField(
        queryset = Produit.objects.all(),
        widget=forms.Select(attrs={'class': 'select-input'}),
        label='Produit'
    )

    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.all(),
        widget=forms.Select(attrs={'class': 'select-input'}),
        label='Fournisseur'
    )

    quantite = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class':'text-input'}),
        label= 'Quantité'
    )

    prix = forms.DecimalField(
        max_digits=10,
        decimal_places=2,

        widget=forms.NumberInput(attrs={'class':'text-input'}),
        label= 'Prix Unitaire'
    )
    date_expiration = forms.DateField(
    label="Date d’expiration (optionnel)",
    required=False,
    widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

class ApprovisionnementForm0(forms.Form):
    codes_barres = forms.CharField(
        label="Scanner le code-barres", 
        required=False, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Scannez un code-barres...',
            'id': 'barcodeInput'
        })
    )

    quantite = forms.IntegerField(
        label="Quantité à ajouter",
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantité'
        })
    )

    prix_achat = forms.DecimalField(
        label="Prix d’achat unitaire",
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix d’achat'
        })
    )

    prix_vente = forms.DecimalField(
        label="Prix de vente unitaire",
        max_digits=10, decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Prix de vente'
        })

    )

    fournisseur = forms.ModelChoiceField(
        label="Fournisseur",
        queryset=Fournisseur.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_expiration = forms.DateField(
        label="Date d’expiration (optionnel)",
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )


    # CATEGORIE DE PRODUITS

class CategorieForm(forms.ModelForm):
    class Meta:
        model = CategorieProduit
        fields = ['nom', 'description']  # adapte selon ton modèle
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control','rows':'1'})
        }