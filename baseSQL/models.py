# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.utils import timezone
from datetime import timedelta


class Utilisateur(AbstractUser):

    ROLE_CHOICES= [
        ('admin', 'Administrateur'),
        ('caissier','Caissier'),
    ]
    last_activity = models.DateTimeField(null=True, blank=True)
    id_utilisateur = models.AutoField(primary_key=True)
    contact = models.CharField(max_length=250, unique=True)
    adresse = models.CharField(max_length=100)
    email =models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default='caissier')
    statut = models.CharField(max_length=7)
    photo = models.ImageField(upload_to='accounts/', null=True, blank=True)
    ##fist_login= models.BooleanField(default=True)


    def __str__(self):
        return self.username
    @property
    def is_online(self):
        if self.last_activity:
            return timezone.now() - self.last_activity < timedelta(seconds=30)
        return False
    
    class Meta:
        managed = True
        db_table = 'utilisateur'

class ProfilCaissier(models.Model):
    utilisateur = models.OneToOneField('baseSQL.Utilisateur', on_delete=models.CASCADE)
    first_login= models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'profil_caissier'
class Approvisionnement(models.Model):
    id_appro = models.AutoField(primary_key=True)
    id_utilisateur = models.ForeignKey('baseSQL.Utilisateur', models.DO_NOTHING, db_column='id_utilisateur')
    id_frs = models.ForeignKey('Fournisseur', models.DO_NOTHING, db_column='id_frs')
    date = models.DateTimeField()
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_expiration = models.DateField(null=True, blank=True)  

    def est_proche_expiration(self):
        if self.date_expiration:
            delta = (self.date_expiration - date.today()).days
            return 0 < delta <= 7
        return False

    def est_expire(self):
        if self.date_expiration:
            return self.date_expiration < date.today()
        return False

    class Meta:
        managed = True
        db_table = 'approvisionnement'


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entrée', 'Entrée'),
        ('sortie','Sortie'),
        ('retour', 'Retour'),
        ('ajustement', 'Ajustement'),
        ('aprovisionement','Approvisionement'),
        ('transfert','Transfert'),
    ]

    produit = models.ForeignKey('baseSQL.Produit', on_delete=models.CASCADE)
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    utilisateur  =  models.ForeignKey('baseSQL.Utilisateur', on_delete=models.SET_NULL, null=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)
    commentaire= models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"
    class Meta:
        managed = True
        db_table = 'mouvement_stock'        

class Vente(models.Model):
    id_vente = models.AutoField(primary_key=True)
    id_client = models.ForeignKey('baseSQL.Client', models.DO_NOTHING, db_column='id_client')
    id_utilisateur = models.ForeignKey('baseSQL.Utilisateur', models.DO_NOTHING, db_column='id_utilisateur', related_name='ventes')
    date_vente = models.DateTimeField()
    montanttotal = models.DecimalField(db_column='montantTotal', max_digits=10, decimal_places=2)  # Field name made lowercase.
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")

    statut = models.CharField(max_length=10)

    class Meta:
        managed = True
        db_table = 'vente'


class Commande(models.Model):
    id_commande = models.AutoField(primary_key=True)
    id_client= models.ForeignKey('baseSQL.Client', models.DO_NOTHING, db_column='id_client')
    id_utilisateur = models.ForeignKey('baseSQL.Utilisateur', models.DO_NOTHING, db_column='id_utilisateur')
    id_frs= models.ForeignKey('baseSQL.Fournisseur', models.DO_NOTHING, db_column='id_frs')

    date_commande = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'commande'        


class CategorieProduit(models.Model):
    id_categorie = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.nom
    class Meta:
        managed = True
        db_table = 'categorie_produit'

class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True)
    categorie = models.ForeignKey('baseSQL.CategorieProduit', on_delete=models.CASCADE)
    nom_produit = models.CharField(max_length=100)
    codes_barres = models.CharField(max_length=100, unique=True, null=True, blank=True)
    reference = models.CharField(max_length=100)
    description = models.TextField()
    quantite = models.IntegerField()
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actuel = models.IntegerField()
    stock_min = models.IntegerField()
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    def __str__(self):
        return f"{self.nom_produit} ({self.reference})"
    class Meta:
        managed = True
        db_table = 'produit'        



class Client(models.Model):
    id_client = models.AutoField(primary_key=True)
    nom_client = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True,blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    point = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.nom_client} - {self.contact}"
    
    class Meta:
        managed = True
        db_table = 'client'




class Facture(models.Model):
    id_facture = models.AutoField(primary_key=True)
    id_vente = models.ForeignKey('Vente', models.DO_NOTHING, db_column='id_vente')
    code_facture = models.CharField(max_length=100)
    date_emission = models.DateTimeField()
    date_paiement = models.DateTimeField()
    montant_ht = models.DecimalField(db_column='montant_HT', max_digits=10, decimal_places=2)  # Field name made lowercase.
    montant_ttc = models.DecimalField(db_column='montant_TTC', max_digits=10, decimal_places=2)  # Field name made lowercase.
    montant_net = models.DecimalField(max_digits=10, decimal_places=2)
    mode_paiement = models.CharField(max_length=11)

    class Meta:
        managed = True
        db_table = 'facture'


class Fournisseur(models.Model):
    id_frs = models.AutoField(primary_key=True)
    nom_frs = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    adresse = models.CharField(max_length=100)
    pays = models.CharField(max_length=100)
    type_frs = models.CharField(max_length=11)

    def __str__(self):
        return f"{self.nom_frs}"
    class Meta:
        managed = True
        db_table = 'fournisseur'


class LigneAppro(models.Model):
    id_ligneappro = models.AutoField(db_column='id_ligneAppro', primary_key=True)  # Field name made lowercase.
    id_appro = models.ForeignKey('baseSQL.Approvisionnement', models.DO_NOTHING, db_column='id_appro')
    id_produit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='id_produit')
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=0)

    class Meta:
        managed = True
        db_table = 'ligne_appro'


class LigneCommande(models.Model):
    id_lignecmd = models.AutoField(db_column='id_ligneCmd', primary_key=True)  # Field name made lowercase.
    id_commande = models.ForeignKey('baseSQL.Commande', models.DO_NOTHING, db_column='id_commande')
    id_produit = models.ForeignKey('Produit', models.DO_NOTHING, db_column='id_produit')
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'ligne_commande'


class LigneVente(models.Model):
    id_ligne = models.AutoField(primary_key=True)
    id_vente = models.ForeignKey('baseSQL.Vente', models.DO_NOTHING, db_column='id_vente')
    id_produit = models.ForeignKey('baseSQL.Produit', models.DO_NOTHING, db_column='id_produit')
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_retournee = models.PositiveIntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'ligne_vente'





class Stock(models.Model):
    id_stock = models.AutoField(primary_key=True)
    id_produit = models.ForeignKey('baseSQL.Produit', models.DO_NOTHING, db_column='id_produit')
    sueil_alerte = models.IntegerField()
    quantite = models.IntegerField()
    date = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'stock'
        
class RetourProduit(models.Model):
    id_retour = models.AutoField(primary_key=True)
    vente = models.ForeignKey('baseSQL.Vente', on_delete=models.CASCADE, db_column='id_vente')
    utilisateur = models.ForeignKey('baseSQL.Utilisateur', on_delete=models.SET_NULL, null=True, db_column='id_utilisateur')
    date_retour = models.DateTimeField(auto_now_add=True)
    raison = models.TextField(blank=True, null=True)
    montant_total_rembourse = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Retour {self.id_retour} - Vente {self.vente.id_vente}"

    class Meta:
        managed = True
        db_table = 'retour_produit'


class LigneRetour(models.Model):
    id_ligne_retour = models.AutoField(primary_key=True)
    retour = models.ForeignKey('baseSQL.RetourProduit', on_delete=models.CASCADE, db_column='id_retour', related_name='lignes_retour')
    produit = models.ForeignKey('baseSQL.Produit', on_delete=models.DO_NOTHING, db_column='id_produit')
    quantite = models.IntegerField()
    prix_rembourse_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'ligne_retour'



