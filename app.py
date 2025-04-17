from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Contact, HistoriqueContact
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///renovation.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'votre_cle_secrete'

db.init_app(app)

# Création des tables à l'initialisation de l'application
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    """Page d'accueil - Liste des contacts"""
    contacts = Contact.query.order_by(Contact.date_creation.desc()).all()
    return render_template('liste_contacts.html', contacts=contacts)

@app.route('/contact/nouveau', methods=['GET', 'POST'])
def nouveau_contact():
    """Page de création d'un nouveau contact"""
    if request.method == 'POST':
        # Récupération des données du formulaire
        contact = Contact(
            nom_prenom=request.form.get('nom_prenom', ''),
            telephone=request.form.get('telephone', ''),
            email=request.form.get('email', ''),
            origine=request.form.get('origine', ''),
            rue=request.form.get('rue', ''),
            numero=request.form.get('numero', ''),
            etage_boite=request.form.get('etage_boite', ''),
            zones=','.join(request.form.getlist('zones')) if request.form.getlist('zones') else '',
            statut=request.form.get('statut', ''),
            futur='futur' in request.form,
            type_bien=request.form.get('type_bien', ''),
            copropriete=','.join(request.form.getlist('copropriete')) if request.form.getlist('copropriete') else '',
            nb_unites=request.form.get('nb_unites', 0) if request.form.get('nb_unites') else 0,
            total_unites=request.form.get('total_unites', 0) if request.form.get('total_unites') else 0,
            revenus=request.form.get('revenus', ''),
            composition_familiale=request.form.get('composition_familiale', ''),
            famille_nombreuse='famille_nombreuse' in request.form,
            fracture_numerique='fracture_numerique' in request.form,
            demande_initiale=request.form.get('demande_initiale', ''),
            thematiques=','.join(request.form.getlist('thematiques')) if request.form.getlist('thematiques') else '',
            type_travaux=','.join(request.form.getlist('type_travaux')) if request.form.getlist('type_travaux') else '',
            primes_introduites=','.join(request.form.getlist('primes_introduites')) if request.form.getlist('primes_introduites') else ''
        )
        
        db.session.add(contact)
        db.session.commit()
        
        # Gestion de l'historique des contacts si des données sont présentes
        date_contact = request.form.get('date_contact')
        type_contact = request.form.get('type_contact')
        
        if date_contact and type_contact:
            historique = HistoriqueContact(
                contact_id=contact.id,
                date=datetime.strptime(date_contact, '%Y-%m-%d').date(),
                type_contact=type_contact,
                interventions=','.join(request.form.getlist('interventions')) if request.form.getlist('interventions') else '',
                commentaire=request.form.get('commentaire', '')
            )
            db.session.add(historique)
            db.session.commit()
        
        flash('Contact ajouté avec succès!', 'success')
        return redirect(url_for('index'))
    
    return render_template('fiche_contact.html')

@app.route('/contact/<int:contact_id>', methods=['GET', 'POST'])
def modifier_contact(contact_id):
    """Page de modification d'un contact existant"""
    contact = Contact.query.get_or_404(contact_id)
    
    if request.method == 'POST':
        # Mise à jour des données du contact
        contact.nom_prenom = request.form.get('nom_prenom', '')
        contact.telephone = request.form.get('telephone', '')
        contact.email = request.form.get('email', '')
        contact.origine = request.form.get('origine', '')
        contact.rue = request.form.get('rue', '')
        contact.numero = request.form.get('numero', '')
        contact.etage_boite = request.form.get('etage_boite', '')
        contact.zones = ','.join(request.form.getlist('zones')) if request.form.getlist('zones') else ''
        contact.statut = request.form.get('statut', '')
        contact.futur = 'futur' in request.form
        contact.type_bien = request.form.get('type_bien', '')
        contact.copropriete = ','.join(request.form.getlist('copropriete')) if request.form.getlist('copropriete') else ''
        contact.nb_unites = request.form.get('nb_unites', 0) if request.form.get('nb_unites') else 0
        contact.total_unites = request.form.get('total_unites', 0) if request.form.get('total_unites') else 0
        contact.revenus = request.form.get('revenus', '')
        contact.composition_familiale = request.form.get('composition_familiale', '')
        contact.famille_nombreuse = 'famille_nombreuse' in request.form
        contact.fracture_numerique = 'fracture_numerique' in request.form
        contact.demande_initiale = request.form.get('demande_initiale', '')
        contact.thematiques = ','.join(request.form.getlist('thematiques')) if request.form.getlist('thematiques') else ''
        contact.type_travaux = ','.join(request.form.getlist('type_travaux')) if request.form.getlist('type_travaux') else ''
        contact.primes_introduites = ','.join(request.form.getlist('primes_introduites')) if request.form.getlist('primes_introduites') else ''
        
        db.session.commit()
        
        # Gestion de l'ajout d'un nouvel historique de contact
        date_contact = request.form.get('date_contact')
        type_contact = request.form.get('type_contact')
        
        if date_contact and type_contact:
            historique = HistoriqueContact(
                contact_id=contact.id,
                date=datetime.strptime(date_contact, '%Y-%m-%d').date(),
                type_contact=type_contact,
                interventions=','.join(request.form.getlist('interventions')) if request.form.getlist('interventions') else '',
                commentaire=request.form.get('commentaire', '')
            )
            db.session.add(historique)
            db.session.commit()
        
        flash('Contact mis à jour avec succès!', 'success')
        return redirect(url_for('index'))
    
    return render_template('fiche_contact.html', contact=contact)

@app.route('/contact/supprimer/<int:contact_id>', methods=['POST'])
def supprimer_contact(contact_id):
    """Suppression d'un contact"""
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    
    flash('Contact supprimé avec succès!', 'success')
    return redirect(url_for('index'))

@app.route('/historique/supprimer/<int:historique_id>', methods=['POST'])
def supprimer_historique(historique_id):
    """Suppression d'un élément de l'historique des contacts"""
    historique = HistoriqueContact.query.get_or_404(historique_id)
    contact_id = historique.contact_id
    
    db.session.delete(historique)
    db.session.commit()
    
    flash('Entrée d\'historique supprimée avec succès!', 'success')
    return redirect(url_for('modifier_contact', contact_id=contact_id))

if __name__ == '__main__':
    app.run(debug=True)
