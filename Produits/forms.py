from django import forms
from baseSQL.models import Produit, CategorieProduit

#FORMULAIRED'AJOUT DEPRODUIT
class ProduitForm (forms.ModelForm):
    categorie = forms.ModelChoiceField(
        queryset=CategorieProduit.objects.all(),
        empty_label="selectionnez une categorie",
        widget=forms.Select(attrs={'class':'form-control'})
     )
    
    codes_barres = forms.CharField(
        required=False,
        widget= forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Scannez le codes-barres'
        })
    )
    class Meta:
        model = Produit
        fields = ['nom_produit', 'reference',  'description', 'quantite', 
                  'prix_achat', 'prix_vente', 'stock_actuel','stock_min', 'categorie', 'image', 'codes_barres']
       
        
        widgets = {
            'nom_produit' : forms.TextInput(attrs={'class': 'from-control'}),
            
            'reference' : forms.TextInput(attrs={'class': 'from-control', 'rows':2}),
            'description': forms.Textarea(attrs={'class': 'from-control', 'rows':2}),
            'quantite': forms.NumberInput(attrs={'class': 'from-control'}),
            'prix_achat': forms.NumberInput(attrs={'class': 'from-control'}),
            'prix_vente' : forms.NumberInput(attrs={'class': 'from-control'}),
            'stock_actuel':  forms.NumberInput(attrs={'class': 'from-control'}),
            'stock_min': forms.NumberInput(attrs={'class': 'from-control'}),
            ##'image': forms.ImageField(),
            'image': forms.FileInput()

        }

    def clean_codes_barres(self):
        codes_barres = self.cleaned_data.get('codes_barres')
        if codes_barres:
            # Exclure l'instance en cours (modification)
            qs = Produit.objects.filter(codes_barres=codes_barres)
            if self.instance.pk:
                 qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise forms.ValidationError("Ce code-barres est déjà utilisé par un autre produit.")
        return codes_barres