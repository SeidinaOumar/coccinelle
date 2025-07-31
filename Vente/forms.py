from django import forms
from baseSQL.models import Vente, LigneVente, Produit

class ClientForm(forms.Form):
    produit = forms.ModelChoiceField(queryset=Produit.objects.all(), label="Produit")
    quantite = forms.IntegerField(min_value=1, label="Quantité")
    prix_unitaire = forms.FloatField(min_value=0.0, label="Prix unitaire")

    def clean(self):
        cleaned_data = super().clean()
        produit = cleaned_data.get("produit")
        quantite = cleaned_data.get("quantite")

        if produit and quantite:
            if quantite > produit.quantite:
                raise forms.ValidationError(
                    f"La quantité demandée ({quantite}) dépasse le stock disponible ({produit.stock_actuel}) pour {produit.nom_produit}."
                )
        return cleaned_data


class VenteForm(forms.ModelForm):
    class Meta:
        model = Vente
        fields = ['id_client']
