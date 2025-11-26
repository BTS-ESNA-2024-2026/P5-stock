# CAHIER DES CHARGES FONCTIONNEL
## Système de Gestion Logistique Militaire (SGLM)

**Version:** 1.0  
**Date:** 24 Novembre 2025  
**Classification:** CONFIDENTIEL DÉFENSE  
**Conformité:** ANSSI, RGS**, RGAA, ISO 27001

---

## TABLE DES MATIÈRES

1. [CONTEXTE ET OBJECTIFS](#1-contexte-et-objectifs)
2. [PÉRIMÈTRE FONCTIONNEL](#2-périmètre-fonctionnel)
3. [EXIGENCES DÉTAILLÉES](#3-exigences-détaillées)
4. [CAS D'UTILISATION](#4-cas-dutilisation)
5. [ARCHITECTURE TECHNIQUE](#5-architecture-technique)
6. [SÉCURITÉ ET CONFORMITÉ ANSSI](#6-sécurité-et-conformité-anssi)
7. [HAUTE DISPONIBILITÉ](#7-haute-disponibilité)
8. [PLANNING ET JALONS](#8-planning-et-jalons)
9. [ANNEXES](#9-annexes)

---

## 1. CONTEXTE ET OBJECTIFS

### 1.1 Contexte

La base militaire gère actuellement ses stocks et sa flotte de véhicules de façon partiellement manuelle, entraînant :
- Erreurs de suivi et pertes de traçabilité
- Ruptures de stock critiques
- Visibilité limitée sur les ressources déployées
- Temps de réponse opérationnelle rallongé
- Non-conformité avec les standards de sécurité ANSSI

### 1.2 Objectifs stratégiques

**[EF-001-P]** Centraliser la gestion complète des stocks (armement, munitions, rations, équipements de protection, véhicules) dans un système unique et sécurisé.

**[EF-002-P]** Assurer un suivi en temps réel avec alertes automatiques sur seuils critiques et anomalies.

**[EF-003-P]** Implémenter une gestion fine des droits d'accès basée sur les rôles (RBAC) conforme aux normes militaires.

**[EF-004-I]** Générer automatiquement des rapports d'utilisation, prévisions de besoins et analyses décisionnelles.

**[EF-005-P]** Garantir la disponibilité du système 24/7 avec un taux de disponibilité ≥ 99.9%.

### 1.3 Périmètre opérationnel

- **Utilisateurs cibles:** 50-200 utilisateurs simultanés
- **Volume de données:** ~100 000 enregistrements matériels
- **Déploiement:** Infrastructure cloud privé ou hybride sécurisé
- **Zones géographiques:** Multi-sites avec synchronisation temps réel

---

## 2. PÉRIMÈTRE FONCTIONNEL

### 2.1 Modules fonctionnels

| Module | Fonctionnalités | Rôles autorisés |
|--------|-----------------|-----------------|
| **Gestion des utilisateurs** | CRUD comptes, assignation rôles, MFA, gestion sessions | Admin |
| **Stocks de matériel** | CRUD équipements, suivi quantités, historique, alertes seuils, inventaire | Admin (r/w), Logisticien (r/w), Utilisateur (r) |
| **Gestion des véhicules** | Suivi état, planning maintenance, affectation missions, géolocalisation | Admin (r/w), Logisticien (r/w), Utilisateur (r) |
| **Opérations logistiques** | Création missions, affectation ressources, suivi temps réel, clôture | Admin (r/w), Logisticien (r/w) |
| **Tableaux de bord** | KPI, visualisations, rapports CSV/PDF, prévisions | Tous (lecture) |
| **Sécurité & audit** | MFA, chiffrement, logs détaillés, conformité ANSSI | Admin |

### 2.2 Entités principales

- **GP (Groupes):** Gestion des groupes et permissions
- **Users:** Utilisateurs avec rôles et authentification
- **Weapon / WeaponType:** Armements et typologie
- **Ammo / AmmoType:** Munitions et classifications
- **MRE / MREType:** Rations de combat
- **Vehicles / VehiclesType:** Flotte de véhicules
- **PP / PPType:** Équipements de protection personnelle
- **Missions:** Opérations logistiques
- **Localisation:** Emplacements physiques (bâtiments, salles, sections)
- **Logs:** Historiques d'actions (matériel et administration)

---

## 3. EXIGENCES DÉTAILLÉES

### 3.1 Exigences Fonctionnelles [EF]

#### 3.1.1 Gestion des utilisateurs

**[EF-101-P]** Le système doit permettre aux administrateurs de créer, modifier, désactiver et supprimer des comptes utilisateurs.

**[EF-102-P]** Chaque utilisateur doit être assigné à un groupe (GP) avec des permissions spécifiques.

**[EF-103-P]** Les rôles disponibles sont : ADMIN, USER, READONLY, MODERATOR.

**[EF-104-P]** L'authentification multi-facteurs (MFA) doit être obligatoire pour les rôles ADMIN et MODERATOR.

**[EF-105-I]** Le système doit enregistrer la date de dernière connexion (lastLogin) pour chaque utilisateur.

**[EF-106-I]** Les sessions utilisateur doivent expirer après 30 minutes d'inactivité.

**[EF-107-S]** Une fonctionnalité de récupération de mot de passe sécurisée doit être disponible.

#### 3.1.2 Gestion des stocks d'armement

**[EF-201-P]** Le système doit permettre l'enregistrement de chaque arme avec son numéro de série (SN) unique.

**[EF-202-P]** Chaque arme doit être associée à un type (WeaponType) définissant : nom, description, type, calibre, marque.

**[EF-203-P]** Le statut de chaque arme doit être tracé : AVAILABLE, IN_USE, MAINTENANCE, RETIRED, DAMAGED, LOST.

**[EF-204-P]** Les dates de révision (lastRevision, nextRevision) doivent être enregistrées et surveillées.

**[EF-205-I]** Une alerte automatique doit être générée 30 jours avant une révision planifiée.

**[EF-206-P]** La localisation précise (bâtiment, salle, section) de chaque arme doit être enregistrée.

**[EF-207-I]** Un historique des mouvements doit être maintenu dans LogMatos.

#### 3.1.3 Gestion des munitions

**[EF-301-P]** Le système doit gérer les stocks de munitions avec quantités en temps réel.

**[EF-302-P]** Chaque lot de munitions doit être typé (calibre, type de balle, type d'explosif, marque).

**[EF-303-P]** Les conditions de stockage doivent être enregistrées et surveillées.

**[EF-304-P]** Une alerte doit être émise lorsque les quantités descendent sous le seuil critique défini.

**[EF-305-I]** Les dates de création et de péremption doivent être tracées.

**[EF-306-I]** Un rapport mensuel de consommation de munitions doit être généré automatiquement.

#### 3.1.4 Gestion des rations (MRE)

**[EF-401-P]** Le système doit gérer les rations de combat avec classification (halal, végétarien).

**[EF-402-P]** Les allergènes et contre-indications doivent être enregistrés pour chaque type.

**[EF-403-I]** Les conditions de stockage et dates de perception doivent être tracées.

**[EF-404-I]** Une alerte doit être générée pour les rations approchant de leur date limite.

#### 3.1.5 Gestion des véhicules

**[EF-501-P]** Chaque véhicule doit être identifié par un numéro de châssis et une plaque d'immatriculation uniques.

**[EF-502-P]** Le système doit suivre le kilométrage et l'historique de maintenance de chaque véhicule.

**[EF-503-P]** Les dates de dernière et prochaine maintenance doivent déclencher des alertes automatiques.

**[EF-504-I]** Un historique détaillé (VehiclesHistory) doit enregistrer : date, lieu, description, coût des interventions.

**[EF-505-I]** Le statut de disponibilité doit être mis à jour en temps réel : AVAILABLE, IN_USE, MAINTENANCE, RETIRED.

**[EF-506-S]** Une fonctionnalité de géolocalisation des véhicules en mission doit être intégrée.

#### 3.1.6 Gestion des équipements de protection (PP)

**[EF-601-P]** Le système doit gérer les équipements de protection personnelle avec tailles et certifications.

**[EF-602-P]** Les normes et certifications (NIJ, STANAG, etc.) doivent être enregistrées.

**[EF-603-I]** Les équipements obligatoires doivent être identifiés avec un flag "mandatory".

**[EF-604-I]** Les dates de perception et conditions de stockage doivent être tracées.

#### 3.1.7 Gestion des missions

**[EF-701-P]** Les utilisateurs autorisés doivent pouvoir créer des missions avec : nom, description, théâtre d'opération, dates.

**[EF-702-P]** Le système doit permettre l'affectation de matériel et véhicules à chaque mission via la table MM.

**[EF-703-P]** Le statut des missions doit être suivi : PLANNED, ACTIVE, COMPLETED, CANCELLED, POSTPONED.

**[EF-704-I]** Un historique des modifications (missionHistory) doit être maintenu.

**[EF-705-I]** Le créateur de la mission doit être enregistré (creatorName, creatorId).

**[EF-706-I]** À la clôture d'une mission, un rapport automatique doit être généré.

#### 3.1.8 Logs et audit

**[EF-801-P]** Toutes les actions sur le matériel doivent être enregistrées dans LogMatos avec : utilisateur, action, description, date.

**[EF-802-P]** Toutes les actions administratives doivent être enregistrées dans LogAdmin.

**[EF-803-P]** Les logs doivent être immuables et horodatés avec précision.

**[EF-804-I]** Les logs doivent être conservés pendant au moins 5 ans.

**[EF-805-I]** Une interface de recherche et filtrage des logs doit être disponible pour les administrateurs.

#### 3.1.9 Tableaux de bord et rapports

**[EF-901-P]** Le système doit afficher un tableau de bord avec KPI en temps réel :
  - Taux de rotation des stocks
  - Niveaux de stock actuels vs. seuils
  - Disponibilité de la flotte de véhicules
  - Missions actives et planifiées

**[EF-902-I]** Les rapports doivent être exportables en CSV et PDF.

**[EF-903-I]** Des graphiques de tendances et prévisions doivent être générés automatiquement.

**[EF-904-S]** Un module de planification prévisionnelle basé sur l'historique doit être disponible.

---

### 3.2 Exigences Techniques [ET]

#### 3.2.1 Architecture

**[ET-101-P]** L'application doit utiliser une architecture microservices containerisée avec Docker.

**[ET-102-P]** Le backend doit être développé avec Next.js 14+ (App Router avec API Routes) et TypeScript.

**[ET-102-A]** Next.js sera utilisé en mode fullstack :
  - Frontend : React Server Components (RSC) + Client Components
  - Backend : API Routes dans `/app/api/`
  - Possibilité de déployer des microservices Next.js séparés par domaine métier

**[ET-103-P]** Le frontend doit être une SPA (React/Vue.js/Angular) responsive.

**[ET-104-P]** La base de données doit être MySQL 8.0+ avec Prisma ORM.

**[ET-105-I]** Une API RESTful ou GraphQL doit exposer les fonctionnalités.

**[ET-106-I]** L'application doit être compatible avec les navigateurs modernes (Chrome, Firefox, Edge).

#### 3.2.2 Performance

**[ET-201-P]** Le temps de réponse pour les requêtes standards doit être < 500ms.

**[ET-202-P]** Le système doit supporter au moins 200 utilisateurs simultanés.

**[ET-203-I]** Les requêtes de recherche complexes doivent retourner des résultats en < 2s.

**[ET-204-I]** Les exports de rapports volumineux doivent être traités en arrière-plan (jobs asynchrones).

#### 3.2.3 Scalabilité

**[ET-301-P]** L'architecture doit permettre une scalabilité horizontale via Kubernetes.

**[ET-302-I]** Le système doit gérer une croissance de 20% des données annuellement.

**[ET-303-I]** Un système de cache (Redis) doit être implémenté pour optimiser les performances.

#### 3.2.4 Base de données

**[ET-402-P]** Des triggers doivent automatiser :
  - Mise à jour des alertes de seuil
  - Calcul des KPI en temps réel
  - Validation de l'intégrité référentielle

**[ET-402-A]** Configuration MySQL optimisée pour la performance :
  - InnoDB buffer pool : 70-80% de la RAM disponible
  - Query cache activé pour requêtes répétitives
  - Index FULLTEXT pour recherches textuelles
  - Partitionnement des tables de logs par date

**[ET-403-P]** Des vues matérialisées doivent être créées pour les rapports fréquents.

**[ET-404-P]** Un système de backup automatique doit être configuré (quotidien avec rétention 30 jours).

---

### 3.3 Exigences de Sécurité [ES] - Conformité ANSSI

#### 3.3.1 Authentification

**[ES-101-P]** L'authentification doit utiliser un mécanisme robuste (bcrypt/argon2) pour le hachage des mots de passe avec salt unique.

**[ES-102-P]** La politique de mots de passe doit imposer :
  - Minimum 12 caractères
  - Majuscules, minuscules, chiffres, caractères spéciaux
  - Pas de réutilisation des 10 derniers mots de passe
  - Rotation obligatoire tous les 90 jours

**[ES-103-P]** L'authentification multi-facteurs (TOTP ou U2F) doit être obligatoire pour les rôles ADMIN MODERATOR et USER.

**[ES-104-P]** Les tentatives de connexion échouées doivent être limitées (5 tentatives max, blocage 15 minutes).

**[ES-105-I]** Un mécanisme anti-brute force avec CAPTCHA doit être implémenté après 3 échecs.

**[ES-106-P]** Les sessions doivent utiliser des tokens JWT signés avec RS256 (clés RSA 4096 bits minimum).

**[ES-107-P]** Le refresh token doit être stocké de manière sécurisée (HttpOnly, Secure, SameSite cookies).

**[ES-108-I]** Une détection d'activité suspecte (connexions depuis nouveaux appareils/localisations) doit alerter l'utilisateur.

#### 3.3.2 Autorisation et contrôle d'accès

**[ES-201-P]** Le modèle RBAC (Role-Based Access Control) doit être strictement appliqué au niveau API et UI.

**[ES-202-P]** Les permissions doivent être vérifiées à chaque requête (pas de confiance côté client).

**[ES-203-P]** Le principe du moindre privilège doit être appliqué pour chaque rôle.

**[ES-204-I]** Une matrice de droits détaillée doit être documentée et auditée trimestriellement.

#### 3.3.3 Chiffrement des données

**[ES-301-P]** Toutes les communications doivent utiliser TLS 1.3 minimum avec certificats valides.

**[ES-302-P]** Les données sensibles en base de données doivent être chiffrées au repos (AES-256-GCM).

**[ES-303-P]** Les champs sensibles doivent être chiffrés individuellement :
  - Mots de passe (hachage bcrypt/argon2)
  - Numéros de série sensibles
  - Données personnelles

**[ES-304-P]** La gestion des clés de chiffrement doit suivre les recommandations ANSSI :
  - Rotation annuelle des clés
  - Stockage dans un HSM ou gestionnaire de secrets sécurisé (HashiCorp Vault)
  - Séparation des clés de chiffrement/déchiffrement

**[ES-305-I]** Un mécanisme de chiffrement end-to-end pour les exports sensibles doit être disponible.

#### 3.3.4 Protection contre les attaques

**[ES-401-P]** Protection contre les injections SQL :
  - Utilisation exclusive de requêtes paramétrées (Prisma ORM)
  - Validation stricte des entrées utilisateur
  - Interdiction de requêtes dynamiques non sécurisées

**[ES-402-P]** Protection contre XSS (Cross-Site Scripting) :
  - Sanitisation de toutes les entrées utilisateur
  - Content Security Policy (CSP) stricte
  - Encodage des sorties HTML

**[ES-403-P]** Protection contre CSRF (Cross-Site Request Forgery) :
  - Tokens CSRF pour toutes les actions sensibles
  - Vérification de l'origine des requêtes
  - Cookie SameSite=Strict

**[ES-404-P]** Protection contre les attaques par déni de service (DDoS) :
  - Rate limiting sur les endpoints API (10 req/s par IP)
  - Limitation de taille des requêtes (10MB max)
  - WAF (Web Application Firewall) avec règles OWASP

**[ES-405-P]** Headers de sécurité obligatoires :
  - Strict-Transport-Security
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: no-referrer

**[ES-406-I]** Un système de détection d'intrusion (IDS/IPS) doit analyser le trafic en temps réel.

#### 3.3.5 Audit et traçabilité

**[ES-501-P]** Tous les événements de sécurité doivent être loggés :
  - Authentifications (succès/échec)
  - Modifications de droits
  - Accès aux données sensibles
  - Modifications/suppressions de données
  - Actions administratives

**[ES-502-P]** Les logs de sécurité doivent contenir :
  - Timestamp précis (UTC)
  - Identifiant utilisateur
  - Adresse IP source
  - Action effectuée
  - Résultat (succès/échec)
  - Données concernées (sans données sensibles)

**[ES-503-P]** Les logs doivent être immuables et signés cryptographiquement.

**[ES-504-P]** Les logs doivent être centralisés dans un système SIEM dédié.

**[ES-505-P]** Conservation des logs :
  - Logs de sécurité : 5 ans minimum
  - Logs applicatifs : 1 an minimum
  - Logs de debug : 3 mois

**[ES-506-I]** Des alertes automatiques doivent être configurées pour :
  - Tentatives de connexion suspectes
  - Modifications de droits
  - Accès à des données sensibles en dehors des heures ouvrables
  - Patterns d'attaque détectés

#### 3.3.6 Sauvegarde et restauration

**[ES-601-P]** Sauvegardes automatiques quotidiennes complètes + incrémentielles horaires.

**[ES-602-P]** Les sauvegardes doivent être chiffrées (AES-256) et stockées sur site distant.

**[ES-603-P]** Un test de restauration doit être effectué mensuellement.

**[ES-604-I]** Le RPO (Recovery Point Objective) doit être ≤ 1 heure.

**[ES-605-I]** Le RTO (Recovery Time Objective) doit être ≤ 4 heures.

#### 3.3.7 Conformité réglementaire

**[ES-701-P]** Le système doit être conforme au RGS (Référentiel Général de Sécurité niveau).

**[ES-702-P]** Le système doit respecter les recommandations de l'ANSSI pour les systèmes d'information sensibles.

**[ES-703-I]** Un audit de sécurité externe doit être réalisé annuellement.

**[ES-704-I]** Une certification ISO 27001 doit être obtenue dans les 12 mois suivant le déploiement.

**[ES-705-I]** La conformité RGPD doit être assurée pour les données personnelles.


#### 3.3.8 Sécurité du développement

**[ES-901-P]** Le code doit être analysé par des outils SAST (Static Application Security Testing) à chaque commit.

**[ES-902-P]** Les dépendances doivent être scannées pour les vulnérabilités connues (Dependabot, Snyk).

**[ES-903-P]** Un pipeline CI/CD sécurisé doit bloquer le déploiement en cas de vulnérabilité critique.

**[ES-904-I]** Des tests de pénétration doivent être réalisés semestriellement.

**[ES-905-I]** Une politique de divulgation responsable des vulnérabilités doit être établie.

---

### 3.4 Exigences d'Ergonomie [EE]

**[EE-101-P]** L'interface doit être conforme au RGAA (Référentiel Général d'Amélioration de l'Accessibilité) niveau AA minimum.

**[EE-102-P]** Le design doit être responsive et fonctionnel sur écrans 1024px minimum.

**[EE-103-I]** Les formulaires doivent avoir une validation en temps réel avec messages d'erreur explicites.

**[EE-104-I]** Un mode "Dark Mode" doit être disponible pour réduire la fatigue visuelle.

**[EE-105-I]** Les actions destructives (suppression) doivent requérir une confirmation explicite.

**[EE-106-I]** L'interface doit supporter les raccourcis clavier pour les actions fréquentes.

**[EE-107-S]** Une aide contextuelle (tooltips, documentation inline) doit être disponible.

**[EE-108-S]** L'interface doit être disponible en français et anglais.

---

### 3.5 Exigences de Management et Qualité [EM]

**[EM-101-P]** Le titulaire du contrat doit organiser un comité de pilotage mensuel.

**[EM-102-P]** Un rapport d'avancement détaillé doit être fourni à chaque comité.

**[EM-103-P]** Une documentation technique complète doit être livrée (architecture, API, déploiement, maintenance).

**[EM-104-P]** Une documentation utilisateur détaillée avec captures d'écran doit être fournie.

**[EM-105-I]** Une formation des utilisateurs (admin, logisticien, utilisateur) doit être dispensée.

**[EM-106-I]** Un support technique doit être disponible pendant 6 mois après le déploiement.

**[EM-107-I]** Un plan de test détaillé doit être élaboré et validé avant les phases de recette.

**[EM-108-S]** Des métriques de qualité du code doivent être suivies (couverture de tests > 80%, complexité cyclomatique).

---

## 4. CAS D'UTILISATION

### 4.1 UC-01 : Authentification utilisateur

**Acteur principal:** Utilisateur (tous rôles)  
**Préconditions:** L'utilisateur dispose d'un compte actif  
**Postconditions:** L'utilisateur est authentifié et accède au tableau de bord

**Scénario nominal:**
1. L'utilisateur accède à la page de connexion
2. Le système affiche le formulaire d'authentification
3. L'utilisateur saisit son identifiant et mot de passe
4. Le système valide les credentials
5. Si MFA activé : le système demande le code TOTP
6. L'utilisateur saisit le code MFA
7. Le système valide le code MFA
8. Le système crée une session sécurisée
9. Le système redirige vers le tableau de bord approprié au rôle
10. Le système enregistre la connexion dans les logs

**Scénarios alternatifs:**
- 4a. Credentials invalides : afficher message d'erreur, incrémenter compteur échecs
- 4b. 5 échecs consécutifs : bloquer le compte 15 minutes
- 6a. Code MFA invalide : redemander le code (3 tentatives max)
- 7a. Session expirée : rediriger vers login

### 4.2 UC-02 : Créer un utilisateur

**Acteur principal:** Administrateur  
**Préconditions:** L'administrateur est authentifié  
**Postconditions:** Un nouveau compte utilisateur est créé

**Scénario nominal:**
1. L'administrateur accède au module de gestion des utilisateurs
2. L'administrateur clique sur "Créer un utilisateur"
3. Le système affiche le formulaire de création
4. L'administrateur saisit : username, name, groupe (GP), rôle
5. Le système génère un mot de passe temporaire
6. Le système crée le compte avec statut "Activation requise"
7. Le système envoie les credentials à l'utilisateur (canal sécurisé)
8. Le système enregistre l'action dans LogAdmin
9. Le système affiche une confirmation

**Scénarios alternatifs:**
- 4a. Username déjà existant : afficher erreur, redemander
- 5a. Erreur d'envoi des credentials : logger l'incident, notifier admin

### 4.3 UC-03 : Enregistrer une nouvelle arme

**Acteur principal:** Logisticien  
**Préconditions:** Le logisticien est authentifié avec droits d'écriture  
**Postconditions:** L'arme est enregistrée dans le système

**Scénario nominal:**
1. Le logisticien accède au module "Armement"
2. Le logisticien clique sur "Ajouter une arme"
3. Le système affiche le formulaire
4. Le logisticien sélectionne le type d'arme (WeaponType)
5. Le logisticien saisit : SN, date d'entrée, localisation, statut
6. Le logisticien définit les dates de révision
7. Le système valide l'unicité du SN
8. Le système enregistre l'arme en base
9. Le système enregistre l'action dans LogMatos
10. Le système affiche une confirmation avec QR code de l'arme

**Scénarios alternatifs:**
- 7a. SN déjà existant : afficher erreur, redemander
- 4a. Type d'arme inexistant : proposer de créer le type

### 4.4 UC-04 : Créer une mission et affecter du matériel

**Acteur principal:** Logisticien/Admin  
**Préconditions:** L'acteur est authentifié avec droits appropriés  
**Postconditions:** Une mission est créée avec matériel affecté

**Scénario nominal:**
1. L'acteur accède au module "Missions"
2. L'acteur clique sur "Créer une mission"
3. Le système affiche le formulaire de mission
4. L'acteur saisit : nom, description, théâtre, dates début/fin
5. L'acteur sélectionne le matériel nécessaire (armes, munitions, véhicules, MRE, PP)
6. Le système vérifie la disponibilité du matériel aux dates demandées
7. Le système crée la mission avec statut PLANNED
8. Le système crée les enregistrements MM (Mission-Matériel)
9. Le système met à jour le statut du matériel (IN_USE à la date de début)
10. Le système enregistre l'action dans LogMatos
11. Le système génère une feuille de route PDF
12. Le système envoie des notifications aux parties prenantes

**Scénarios alternatifs:**
- 6a. Matériel indisponible : afficher liste d'alternatives disponibles
- 6b. Chevauchement de dates : proposer réajustement ou autre matériel

### 4.5 UC-05 : Consulter le tableau de bord

**Acteur principal:** Tous utilisateurs  
**Préconditions:** L'utilisateur est authentifié  
**Postconditions:** L'utilisateur visualise les KPI selon ses droits

**Scénario nominal:**
1. L'utilisateur accède au tableau de bord
2. Le système charge les KPI temps réel :
   - Niveau des stocks par catégorie
   - Alertes de seuils critiques
   - Disponibilité de la flotte de véhicules
   - Missions actives
   - Prochaines maintenances/révisions
3. Le système affiche des graphiques interactifs
4. L'utilisateur peut filtrer par période, catégorie, localisation
5. L'utilisateur peut exporter les données (CSV/PDF)

**Scénarios alternatifs:**
- 2a. Erreur de chargement des données : afficher message, proposer rafraîchissement

### 4.6 UC-06 : Générer un rapport de consommation

**Acteur principal:** Admin/Logisticien  
**Préconditions:** L'acteur est authentifié  
**Postconditions:** Un rapport détaillé est généré et exporté

**Scénario nominal:**
1. L'acteur accède au module "Rapports"
2. L'acteur sélectionne le type de rapport (consommation munitions, utilisation véhicules, etc.)
3. L'acteur définit les critères : période, catégories, filtres
4. Le système interroge la base de données et agrège les données
5. Le système génère le rapport avec visualisations
6. L'acteur prévisualise le rapport
7. L'acteur choisit le format d'export (CSV/PDF)
8. Le système génère le fichier et le met à disposition en téléchargement
9. Le système enregistre l'action dans LogAdmin

**Scénarios alternatifs:**
- 4a. Données volumineuses : traitement asynchrone, notification à la fin

### 4.7 UC-07 : Gérer une alerte de seuil critique

**Acteur principal:** Système (automatique)  
**Acteur secondaire:** Logisticien  
**Préconditions:** Un stock passe sous le seuil critique  
**Postconditions:** Les responsables sont notifiés

**Scénario nominal:**
1. Le système détecte un stock sous le seuil critique (trigger DB)
2. Le système crée une alerte avec niveau de priorité
3. Le système envoie des notifications :
   - Email aux logisticiens concernés
   - Notification in-app
   - SMS si niveau critique élevé (optionnel)
4. Le système affiche l'alerte dans le tableau de bord
5. Le logisticien consulte l'alerte
6. Le logisticien prend les mesures appropriées (commande, réallocation)
7. Le logisticien marque l'alerte comme traitée
8. Le système archive l'alerte

**Scénarios alternatifs:**
- 6a. Aucune action dans les 48h : escalade au niveau supérieur

### 4.8 UC-08 : Planifier une maintenance de véhicule

**Acteur principal:** Logisticien  
**Préconditions:** Le logisticien est authentifié  
**Postconditions:** Une maintenance est planifiée

**Scénario nominal:**
1. Le logisticien accède au module "Véhicules"
2. Le logisticien sélectionne un véhicule
3. Le système affiche l'historique et les détails du véhicule
4. Le logisticien clique sur "Planifier maintenance"
5. Le logisticien saisit : date, type d'intervention, description, coût estimé
6. Le système vérifie la disponibilité du véhicule
7. Le système met à jour nextMaintenance
8. Le système change le statut du véhicule à MAINTENANCE à la date prévue
9. Le système enregistre dans VehiclesHistory
10. Le système crée un rappel automatique 7 jours avant

**Scénarios alternatifs:**
- 6a. Véhicule affecté à une mission : proposer reprogrammation ou autre véhicule

### 4.9 UC-09 : Consulter les logs d'audit

**Acteur principal:** Administrateur  
**Préconditions:** L'administrateur est authentifié  
**Postconditions:** Les logs sont consultés

**Scénario nominal:**
1. L'administrateur accède au module "Audit"
2. Le système affiche l'interface de recherche de logs
3. L'administrateur définit les critères : période, utilisateur, action, type de log
4. Le système interroge LogMatos et LogAdmin
5. Le système affiche les résultats paginés
6. L'administrateur peut exporter les logs (CSV)
7. Le système enregistre la consultation dans LogAdmin

**Scénarios alternatifs:**
- 4a. Aucun résultat : afficher message informatif

### 4.10 UC-10 : Gérer une perte de matériel

**Acteur principal:** Logisticien/Admin  
**Préconditions:** Un matériel est déclaré perdu  
**Postconditions:** Le matériel est marqué LOST, une enquête est lancée

**Scénario nominal:**
1. L'acteur accède à la fiche du matériel concerné
2. L'acteur clique sur "Déclarer perte"
3. Le système affiche un formulaire de déclaration
4. L'acteur saisit : date de constatation, circonstances, rapport
5. Le système change le statut à LOST
6. Le système crée une entrée dans LogMatos
7. Le système génère automatiquement un rapport d'incident
8. Le système notifie les autorités compétentes
9. Le système met à jour les statistiques de pertes

**Scénarios alternatifs:**
- 4a. Matériel sensible (arme) : procédure d'urgence automatique

---

## 5. ARCHITECTURE TECHNIQUE

### 5.1 Architecture globale

```
┌─────────────────────────────────────────────────────────────┐
│                         UTILISATEURS                         │
│              (Navigateurs Web, Mobiles, Tablettes)           │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS/TLS 1.3
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    CLOUDFLARE / WAF                         │
│            (DDoS Protection, Rate Limiting)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  KUBERNETES CLUSTER                         │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              INGRESS CONTROLLER (Nginx)                │ │
│  │              + Certificate Manager (Cert-Manager)      │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │                  FRONTEND (SPA)                        │ │
│  │       React + TypeScript + TailwindCSS                 │ │
│  │       Pods: 3 replicas (AutoScaling)                   │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │ REST/GraphQL API                    │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │                  API GATEWAY                           │ │
│  │         (Authentication, Rate Limiting, Routing)       │ │
│  │                 Pods: 3 replicas                       │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │               MICROSERVICES BACKEND                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │  Auth API    │  │  User API    │  │Stock API    │ │ │
│  │  │  (Next.js)   │  │  (Next.js)   │  │  (Next.js)  │ │ │
│  │  │  Pods: 2     │  │  Pods: 3     │  │  Pods: 3    │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │Vehicle API   │  │Mission API   │  │Report API   │ │ │
│  │  │  (Next.js)   │  │  (Next.js)   │  │  (Next.js)  │ │ │
│  │  │  Pods: 2     │  │  Pods: 3     │  │  Pods: 2    │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────┬───────────────────────────────────┘ │
│                       │                                     │
│  ┌────────────────────▼───────────────────────────────────┐ │
│  │               SHARED SERVICES                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │ │
│  │  │  Redis Cache │  │  RabbitMQ    │  │  MinIO (S3) │ │ │
│  │  │  (Session,   │  │  (Async Jobs)│  │  (Files)    │ │ │
│  │  │   Cache)     │  │              │  │             │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  DATA LAYER (External to K8s)               │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  MySQL Cluster (Primary + 2 Replicas)                  │ │
│  │  + Prisma ORM                                          │ │
│  │  + Encryption at Rest (AES-256)                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  HashiCorp Vault (Secrets Management)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ELK Stack (Logs) / Prometheus + Grafana (Monitoring)  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Stack technique détaillée

**Frontend:**
- Framework: React 18+ avec TypeScript
- Styling: TailwindCSS + shadcn/ui
- State Management: Zustand ou Redux Toolkit
- Routing: React Router v6
- API Client: Axios avec interceptors
- Charts: Recharts ou Chart.js
- Build: Vite
- Tests: Vitest + React Testing Library

**Backend:**
- Framework: Next.js 14+ (App Router avec API Routes)
- Runtime: Node.js + TypeScript
- ORM: Prisma
- Validation: Zod
- Authentication: NextAuth.js v5 (JWT strategy)
- MFA: speakeasy (TOTP) ou @auth/core
- Documentation API: Swagger/OpenAPI ou tRPC
- Tests: Jest + Vitest

**Base de données:**
- SGBD: MySQL 8.0+
- ORM: Prisma
- Migration: Prisma Migrate
- Backup: mysqldump + binary logs

**Infrastructure:**
- Orchestration: Kubernetes (K8s)
- Container Registry: Harbor ou GitLab Registry
- CI/CD: GitLab CI ou GitHub Actions
- Monitoring: Prometheus + Grafana
- Logging: ELK Stack (Elasticsearch, Logstash, Kibana)
- Secrets: HashiCorp Vault
- Reverse Proxy: Nginx Ingress Controller
- Certificats: Cert-Manager (Let's Encrypt)

**Sécurité:**
- WAF: Cloudflare ou ModSecurity
- SIEM: Wazuh ou OSSEC
- Vulnerability Scanning: Trivy, Snyk
- SAST: SonarQube
- Secret Scanning: GitGuardian

### 5.3 Schéma de base de données (déjà fourni dans le document)

Voir section 4.1 du document original pour le schéma Prisma complet.

---

## 6. SÉCURITÉ ET CONFORMITÉ ANSSI

### 6.1 Référentiels applicables

- **RGS** (Référentiel Général de Sécurité) : Niveau **
- **PSSIE** (Politique de Sécurité des Systèmes d'Information de l'État)
- **ANSSI** : Guide d'hygiène informatique, Guide sécurisation d'applications web
- **ISO 27001** : Système de management de la sécurité de l'information
- **OWASP Top 10** : Protection contre les vulnérabilités web courantes

### 6.2 Mesures de sécurité détaillées

#### 6.2.1 Authentification renforcée

- Hachage des mots de passe : **Argon2id** (recommandé ANSSI) ou bcrypt (coût 12+)
- MFA obligatoire : TOTP (RFC 6238) avec applications comme Google Authenticator, Authy
- Support U2F/WebAuthn pour clés de sécurité matérielles (YubiKey)
- Politique de mots de passe stricte appliquée côté serveur
- Rotation obligatoire tous les 90 jours pour comptes privilégiés
- Historique des 10 derniers mots de passe interdit

#### 6.2.2 Protection anti-brute force

a faire

#### 6.2.3 Chiffrement des données

**En transit:**
- TLS 1.3 obligatoire
- Ciphers autorisés : TLS_AES_256_GCM_SHA384, TLS_CHACHA20_POLY1305_SHA256
- Certificats : RSA 4096 bits ou ECDSA P-384
- HSTS activé (max-age=31536000; includeSubDomains; preload)

**Au repos:**
- Base de données : Chiffrement transparent (TDE) avec AES-256-GCM
- Champs sensibles : Chiffrement individuel avec clés dédiées
- Fichiers : Chiffrement côté serveur (MinIO avec KMS)

**Gestion des clés:**
- Stockage dans HashiCorp Vault
- Rotation annuelle automatique
- Clés de chiffrement différentes par environnement (dev/staging/prod)
- Backup des clés sur support physique sécurisé (coffre-fort)

#### 6.2.4 Isolation et segmentation réseau

```
┌─────────────────────────────────────────┐
│         DMZ (Zone Démilitarisée)        │
│  - Frontend (port 443)                  │
│  - API Gateway (port 443)               │
└─────────────┬───────────────────────────┘
              │ Firewall + IPS
              ▼
┌─────────────────────────────────────────┐
│     Zone Applicative (Private)          │
│  - Microservices Backend                │
│  - Redis, RabbitMQ                      │
└─────────────┬───────────────────────────┘
              │ Firewall
              ▼
┌─────────────────────────────────────────┐
│      Zone Données (Highly Private)      │
│  - PostgreSQL                           │
│  - Backup Storage                       │
│  - Vault                                │
└─────────────────────────────────────────┘

Règles firewall :
- Deny all by default
- Allow only necessary ports
- Inter-service communication : mTLS
```

#### 6.2.5 Logs et SIEM

**Architecture de logging:**

```
Application Pods → Fluentd (DaemonSet) → Elasticsearch → Kibana
                                       → Wazuh SIEM → Alertes
```

**Events loggés:**
- Authentification (succès/échec)
- Accès aux ressources sensibles
- Modifications de données
- Actions administratives
- Erreurs applicatives
- Événements de sécurité (tentatives d'intrusion, patterns suspects)

**Alertes configurées:**
- 5 échecs d'authentification en 5 minutes → Alerte niveau 2
- Modification de droits utilisateur → Alerte niveau 3
- Accès base de données hors heures ouvrables → Alerte niveau 2
- Pattern d'attaque SQL injection détecté → Alerte niveau 4 (critique)

#### 6.2.6 Tests de sécurité

**Pipeline DevSecOps:**

```
Code Commit
    ↓
Secret Scanning (GitGuardian)
    ↓
SAST (SonarQube)
    ↓
Dependency Check (Snyk/Trivy)
    ↓
Build Docker Image
    ↓
Container Scanning (Trivy)
    ↓
Deploy to Staging
    ↓
DAST (OWASP ZAP)
    ↓
Validation Security Team
    ↓
Deploy to Production
```

**Tests de pénétration:**
- Semestriels par un organisme certifié
- Scope : Application web, API, infrastructure
- Méthodologie : OWASP Testing Guide, PTES
- Livrables : Rapport détaillé + plan de remédiation

### 6.3 Plan de réponse aux incidents

**Phases:**

1. **Détection** (automatique via SIEM + monitoring)
2. **Analyse** (équipe sécurité évalue la gravité)
3. **Containment** (isolation de la menace)
4. **Éradication** (suppression de la cause racine)
5. **Récupération** (restauration du service)
6. **Post-mortem** (analyse + amélioration)

**Temps de réponse:**
- Incident critique : 15 minutes
- Incident majeur : 1 heure
- Incident mineur : 4 heures

---

## 7. HAUTE DISPONIBILITÉ (HA)

### 7.1 Objectifs de disponibilité

- **SLA cible:** 99.9% (< 8.77h de downtime/an)
- **RPO (Recovery Point Objective):** 1 heure
- **RTO (Recovery Time Objective):** 4 heures

### 7.2 Architecture Kubernetes Haute Disponibilité

#### 7.2.1 Cluster Kubernetes multi-master

```
┌─────────────────────────────────────────────────────────┐
│               Load Balancer (HAProxy/Keepalived)        │
└───────────┬─────────────┬─────────────┬─────────────────┘
            │             │             │
    ┌───────▼──────┐ ┌───▼──────┐ ┌───▼──────┐
    │ Master Node 1│ │Master N 2│ │Master N 3│
    │   (etcd 1)   │ │ (etcd 2) │ │ (etcd 3) │
    └──────────────┘ └──────────┘ └──────────┘
            │             │             │
    ────────┴─────────────┴─────────────┴────────
            │                           │
    ┌───────▼──────┐           ┌───────▼──────┐
    │ Worker Node 1│    ...    │ Worker Node N│
    │  (Apps Pods) │           │  (Apps Pods) │
    └──────────────┘           └──────────────┘
```

**Configuration:**
- 3 master nodes (control plane) dans des zones de disponibilité différentes
- Minimum 3 worker nodes (calcul + stockage)
- etcd en cluster (3+ membres) pour haute disponibilité du state
- Load balancer devant les masters (HA avec Keepalived + VIP)

#### 7.2.2 Stratégies de déploiement

**Rolling Update:**
```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

**Pod Disruption Budget:**
```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: app-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: backend-service
```

#### 7.2.3 Auto-scaling

**Horizontal Pod Autoscaler (HPA):**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

**Cluster Autoscaler:**
- Ajout automatique de worker nodes si pods en pending
- Suppression de nodes sous-utilisés

#### 7.2.4 Répartition multi-zones

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-service
spec:
  replicas: 3
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - backend-service
            topologyKey: topology.kubernetes.io/zone
```

Cette configuration force Kubernetes à répartir les pods sur différentes zones de disponibilité.

### 7.3 Base de données MySQL HA

#### 7.3.1 Architecture Master-Replica

```
┌────────────────┐         ┌────────────────┐
│ MySQL          │ Sync    │ MySQL          │
│ Primary        │◄───────►│ Replica 1      │
│ (Read/Write)   │  Rep    │ (Read-Only)    │
└────────┬───────┘         └────────────────┘
         │ Async Rep
         │
         ▼
┌────────────────┐
│ MySQL          │
│ Replica 2      │
│ (Read-Only)    │
└────────────────┘
```

**Configuration:**
- 1 Primary (lecture/écriture)
- 2+ Replica (lecture seule) avec réplication semi-synchrone
- Réplication semi-synchrone vers Replica 1 (garantie durabilité)
- Réplication asynchrone vers Replica 2 (performance)
- Promotion automatique en cas de panne du Primary (Orchestrator ou ProxySQL)
- GTID (Global Transaction Identifiers) activé pour la réplication

#### 7.3.2 Failover automatique avec Orchestrator

```yaml
# Orchestrator configuration
{
  "MySQLTopologyUser": "orchestrator",
  "MySQLTopologyPassword": "***",
  "MySQLOrchestratorHost": "orchestrator-db",
  "MySQLOrchestratorPort": 3306,
  "MySQLOrchestratorDatabase": "orchestrator",
  "RecoveryPeriodBlockSeconds": 300,
  "RecoveryIgnoreHostnameFilters": [],
  "AutoFailover": true,
  "FailureDetectionPeriodBlockMinutes": 10
}
```

**Mécanisme de failover:**
1. Orchestrator détecte la panne du Primary (via heartbeat)
2. Élection automatique d'un nouveau Primary parmi les Replicas
3. Promotion du Replica élu en Primary (< 30 secondes)
4. Reconfiguration des autres Replicas pour suivre le nouveau Primary
5. Application des clients redirigée automatiquement (via ProxySQL)

#### 7.3.3 Connection Pooling avec ProxySQL

```
Applications → ProxySQL (Connection Pooler) → MySQL
               - Read/Write split
               - Max connections: 1000
               - Default pool size: 20
               - Query caching enabled
```

**Configuration ProxySQL:**
- Détection automatique du Primary/Replicas
- Load balancing des requêtes SELECT sur les Replicas
- Routage des INSERT/UPDATE/DELETE vers le Primary
- Health checks toutes les 2 secondes

### 7.4 Storage persistant

**StorageClass avec réplication:**
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-replicated
provisioner: kubernetes.io/rbd
parameters:
  type: replicated
  replication: "3"
  pool: rbd
  adminId: admin
  adminSecretName: ceph-secret
```

**Persistent Volume Claims:**
- Volumes avec réplication 3x sur différents nodes
- Snapshots automatiques quotidiens
- Backup externe (S3-compatible storage)

### 7.5 Monitoring et alerting

#### 7.5.1 Métriques surveillées

**Infrastructure:**
- CPU, RAM, Disk utilization par node
- Network throughput
- Pod restarts / crashes
- Node status (Ready/NotReady)

**Application:**
- Request rate (req/s)
- Response time (p50, p95, p99)
- Error rate (4xx, 5xx)
- Database connection pool usage
- Queue depth (RabbitMQ)

**Base de données:**
- Replication lag
- Active connections
- Transaction rate / Queries per second
- InnoDB buffer pool hit ratio
- Slow queries
- Table locks

#### 7.5.2 Alertes Prometheus

```yaml
groups:
- name: high_availability
  rules:
  - alert: HighPodRestartRate
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High pod restart rate detected"

  - alert: NodeDown
    expr: up{job="node-exporter"} == 0
    for: 3m
    labels:
      severity: critical
    annotations:
      summary: "Node {{ $labels.instance }} is down"

  - alert: DatabaseReplicationLag
    expr: mysql_slave_status_seconds_behind_master > 60
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "MySQL replication lag > 60s"

  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected (>5%)"
```

### 7.6 Disaster Recovery

#### 7.6.1 Stratégie de backup

**Base de données:**
- Full backup quotidien (00:00 UTC) avec mysqldump ou Percona XtraBackup
- Incremental backup horaire (binary logs)
- Rétention : 30 jours en ligne, 1 an en archive froide
- Stockage : S3-compatible (multi-region)
- Chiffrement : AES-256
- Point-in-time recovery possible via binary logs

**Configurations et secrets:**
- Backup quotidien des ConfigMaps et Secrets Kubernetes
- Versionning dans Git (chiffré avec SOPS ou git-crypt)

**Fichiers utilisateurs:**
- Réplication synchrone sur MinIO/S3 (3 copies minimum)
- Lifecycle policy : archivage > 90 jours

#### 7.6.2 Tests de récupération

**Fréquence:** Mensuel

**Procédure:**
1. Restauration complète en environnement de test
2. Vérification de l'intégrité des données
3. Tests fonctionnels basiques
4. Mesure du RTO/RPO réel
5. Documentation des améliorations nécessaires

#### 7.6.3 Plan de reprise d'activité (PRA)

**Site secondaire:**
- Datacenter distant (> 100 km du site principal)
- Réplication asynchrone continue
- Infrastructure en standby (mode réduit)
- Possibilité d'activation complète en < 4h

**Déclenchement du PRA:**
1. Désastre confirmé sur site principal
2. Activation du site secondaire par le responsable sécurité
3. Promotion des bases de données secondaires
4. Redirection du trafic vers le site secondaire (DNS/Load Balancer)
5. Communication aux utilisateurs
6. Opération en mode dégradé si nécessaire
7. Planification du retour au site principal

---

## 8. PLANNING ET JALONS

### 8.1 Phasage du projet

**Phase 1 : Cadrage et conception (4 semaines)**
- Semaine 1-2 : Ateliers fonctionnels, validation des exigences
- Semaine 3-4 : Conception technique détaillée, architecture sécurité
- Livrable : Dossier d'architecture technique, plan de tests

**Phase 2 : Développement Backend (8 semaines)**
- Sprint 1-2 : Infrastructure K8s, base de données, auth
- Sprint 3-4 : Modules Users, GP, Localisation
- Sprint 5-6 : Modules Weapon, Ammo, MRE, PP
- Sprint 7-8 : Modules Vehicles, Missions, Logs
- Livrable : API complète, documentation Swagger

**Phase 3 : Développement Frontend (6 semaines)**
- Sprint 1-2 : Architecture frontend, composants communs, auth
- Sprint 3-4 : Interfaces gestion stocks, véhicules
- Sprint 5-6 : Interfaces missions, tableaux de bord, rapports
- Livrable : Application web complète

**Phase 4 : Intégration et sécurité (4 semaines)**
- Semaine 1 : Intégration frontend/backend
- Semaine 2 : Hardening sécurité, tests de pénétration
- Semaine 3 : Optimisations performance, HA
- Semaine 4 : Documentation complète
- Livrable : Application intégrée sécurisée

**Phase 5 : Tests et recette (3 semaines)**
- Semaine 1 : Tests unitaires/intégration (objectif 80% couverture)
- Semaine 2 : Tests fonctionnels, UAT avec utilisateurs pilotes
- Semaine 3 : Corrections bugs, tests de non-régression
- Livrable : Rapport de tests, PV de recette

**Phase 6 : Déploiement et formation (2 semaines)**
- Semaine 1 : Déploiement production, migration données
- Semaine 2 : Formation utilisateurs (admin, logisticien, user)
- Livrable : Système en production, utilisateurs formés

**Phase 7 : Support et maintenance (6 mois)**
- Support niveau 1-2-3 garanti
- Corrections de bugs en continu
- Évolutions mineures
- Rapports mensuels

### 8.2 Jalons clés

| Jalon | Date cible | Critère de validation |
|-------|-----------|----------------------|
| **J1 - Kick-off** | S0 | Comité de lancement, équipe constituée |
| **J2 - Conception validée** | S4 | Dossier d'architecture approuvé par le RSSI |
| **J3 - API Backend complète** | S12 | 100% des endpoints développés et testés |
| **J4 - Frontend v1** | S18 | Interfaces principales fonctionnelles |
| **J5 - Sécurité validée** | S22 | Tests de pénétration passés, certification ANSSI en cours |
| **J6 - Recette fonctionnelle** | S25 | PV de recette signé par le MOA |
| **J7 - Mise en production** | S27 | Système accessible en production, données migrées |
| **J8 - Fin de support** | S53 | Transfert de compétences finalisé |

## 9. ANNEXES

### 9.1 Diagrammes UML

#### 9.1.1 Diagramme de classes (simplifié)

```
┌─────────────────┐
│      GP         │
├─────────────────┤
│ + id: Int       │
│ + nom: String   │
│ + perms: String │
└────────┬────────┘
         │ 1
         │
         │ *
┌────────▼────────┐         ┌─────────────────┐
│     Users       │         │    LogAdmin     │
├─────────────────┤         ├─────────────────┤
│ + id: Int       │         │ + id: Int       │
│ + username      │         │ + action        │
│ + hash          │◄───────►│ + date          │
│ + MFA: Boolean  │    *    │                 │
│ + role          │         └─────────────────┘
└────────┬────────┘
         │ 1
         │
         │ *
┌────────▼────────┐
│    LogMatos     │         ┌─────────────────┐
├─────────────────┤    *    │     Matos       │
│ + id: Int       │◄───────►│ (Central)       │
│ + action        │         ├─────────────────┤
│ + description   │         │ + idWeapon      │
│ + date          │         │ + idMRE         │
└─────────────────┘         │ + idAmmo        │
                            │ + idVehicle     │
                            │ + idPP          │
                            └────────┬────────┘
                                     │
                    ┌────────────────┼────────────────┬────────────┐
                    │                │                │            │
           ┌────────▼────────┐ ┌────▼─────┐ ┌────────▼────┐ ┌────▼─────┐
           │     Weapon      │ │   MRE    │ │    Ammo     │ │Vehicles  │
           ├─────────────────┤ ├──────────┤ ├─────────────┤ ├──────────┤
           │ + SN: String    │ │+ status  │ │+ quantity   │ │+ plate   │
           │ + status        │ │+ halal   │ │+ calibre    │ │+ status  │
           │ + nextRevision  │ └──────────┘ └─────────────┘ │+ km      │
           └─────────────────┘                               └──────────┘

┌─────────────────┐         ┌─────────────────┐
│    Missions     │    *    │       MM        │    *    ┌─────────────┐
│                 │◄───────►│ (Mission-Matos) │◄───────►│    Matos    │
├─────────────────┤         ├─────────────────┤         └─────────────┘
│ + name          │         │ + idMission     │
│ + status        │         │ + idMatos       │
│ + dateBeginning │         └─────────────────┘
│ + dateEnd       │
└─────────────────┘

┌─────────────────┐
│  Localisation   │
├─────────────────┤
│ + building      │
│ + room          │
│ + section       │
└────────┬────────┘
         │ 1
         │
         │ *
    ┌────┴───┬──────┬──────┬───────┐
    │        │      │      │       │
┌───▼──┐ ┌──▼──┐ ┌─▼───┐ ┌▼────┐ ┌▼──┐
│Weapon│ │Ammo │ │MRE  │ │Veh  │ │PP │
└──────┘ └─────┘ └─────┘ └─────┘ └───┘
```

#### 9.1.2 Diagramme de séquence - Authentification avec MFA

```
User          Frontend       API Gateway      Auth Service      Database       MFA Service
 │                │               │                │               │                │
 │──Login Form──>│               │                │               │                │
 │                │               │                │               │                │
 │                │──POST /auth/login─────────────>│               │                │
 │                │               │                │               │                │
 │                │               │                │──Check credentials───────────>│
 │                │               │                │<──User found (hash, MFA)──────│
 │                │               │                │               │                │
 │                │               │                │───Verify password──────────────│
 │                │               │                │               │                │
 │                │               │                │──If MFA enabled───────────────>│
 │                │               │                │               │                │
 │                │<──────────────Require MFA code─────────────────│                │
 │<──MFA Prompt──│               │                │               │                │
 │                │               │                │               │                │
 │──Enter TOTP──>│               │                │               │                │
 │                │──POST /auth/verify-mfa────────>│               │                │
 │                │               │                │───Verify TOTP────────────────>│
 │                │               │                │<──Valid───────────────────────│
 │                │               │                │               │                │
 │                │               │                │───Create session──────────────>│
 │                │               │                │<──JWT tokens──────────────────│
 │                │               │                │               │                │
 │                │               │                │───Log success─────────────────>│
 │                │<──────────────JWT + Refresh────────────────────│                │
 │<─Redirect─────│               │                │               │                │
 │  Dashboard    │               │                │               │                │
```


### 9.3 Kanban Board - User Stories / Tasks

#### Epic 1: Authentification et Gestion des Utilisateurs

**TODO:**
- [ ] [US-001] En tant qu'admin, je veux créer un utilisateur avec rôle et groupe
- [ ] [US-002] En tant qu'admin, je veux activer/désactiver le MFA pour un utilisateur
- [ ] [US-003] En tant qu'utilisateur, je veux me connecter avec username/password
- [ ] [US-004] En tant qu'utilisateur avec MFA, je veux valider mon TOTP
- [ ] [US-005] En tant qu'utilisateur, je veux récupérer mon mot de passe oublié

**IN PROGRESS:**
- [ ] [TASK-001] Développer le modèle Prisma Users + GP pour MySQL
- [ ] [TASK-002] Implémenter JWT authentication avec NextAuth.js v5
- [ ] [TASK-003] Intégrer speakeasy pour TOTP

**DONE:**
- [x] [TASK-000] Setup projet Next.js 14+ (App Router) + Prisma + MySQL

#### Epic 2: Gestion des Stocks d'Armement

**TODO:**
- [ ] [US-101] En tant que logisticien, je veux ajouter une nouvelle arme au stock
- [ ] [US-102] En tant que logisticien, je veux modifier les informations d'une arme
- [ ] [US-103] En tant qu'utilisateur, je veux consulter la liste des armes disponibles
- [ ] [US-104] En tant que logisticien, je veux filtrer les armes par statut/type/localisation
- [ ] [US-105] En tant que système, je veux alerter 30j avant une révision d'arme

**IN PROGRESS:**
- [ ] [TASK-101] Développer modèles Weapon + WeaponType
- [ ] [TASK-102] API CRUD weapons avec validation

**DONE:**
- [x] Conception du schéma de données

#### Epic 3: Gestion des Munitions

**TODO:**
- [ ] [US-201] En tant que logisticien, je veux enregistrer un lot de munitions
- [ ] [US-202] En tant que logisticien, je veux mettre à jour la quantité de munitions
- [ ] [US-203] En tant que système, je veux alerter quand quantité < seuil critique
- [ ] [US-204] En tant que logisticien, je veux consulter l'historique de consommation

#### Epic 4: Gestion des Véhicules

**TODO:**
- [ ] [US-301] En tant que logisticien, je veux ajouter un véhicule à la flotte
- [ ] [US-302] En tant que logisticien, je veux planifier une maintenance
- [ ] [US-303] En tant que système, je veux alerter quand nextMaintenance approche
- [ ] [US-304] En tant qu'utilisateur, je veux consulter l'historique d'un véhicule
- [ ] [US-305] En tant que logisticien, je veux voir la disponibilité de la flotte en temps réel

#### Epic 5: Gestion des Missions

**TODO:**
- [ ] [US-401] En tant que logisticien, je veux créer une mission avec dates et théâtre
- [ ] [US-402] En tant que logisticien, je veux affecter du matériel à une mission
- [ ] [US-403] En tant que système, je veux vérifier la disponibilité du matériel
- [ ] [US-404] En tant que logisticien, je veux clôturer une mission et générer un rapport
- [ ] [US-405] En tant qu'utilisateur, je veux consulter les missions actives

#### Epic 6: Tableaux de Bord et Rapports

**TODO:**
- [ ] [US-501] En tant qu'utilisateur, je veux voir un dashboard avec KPI temps réel
- [ ] [US-502] En tant qu'admin, je veux exporter un rapport de consommation en PDF
- [ ] [US-503] En tant que logisticien, je veux voir des prévisions de besoins
- [ ] [US-504] En tant qu'utilisateur, je veux filtrer les données par période

#### Epic 7: Sécurité et Audit

**TODO:**
- [ ] [US-601] En tant qu'admin, je veux consulter les logs d'actions matériel
- [ ] [US-602] En tant qu'admin, je veux consulter les logs d'actions admin
- [ ] [US-603] En tant qu'admin, je veux exporter les logs en CSV
- [ ] [US-604] En tant que système, je veux loguer toutes les actions sensibles
- [ ] [TASK-601] Implémenter chiffrement AES-256 pour données sensibles
- [ ] [TASK-602] Configurer rate limiting anti-brute force
- [ ] [TASK-603] Implémenter CSRF protection
- [ ] [TASK-604] Configurer security headers (HSTS, CSP, etc.)

#### Epic 8: Infrastructure et Haute Disponibilité

**TODO:**
- [ ] [TASK-801] Setup cluster Kubernetes 3 masters + 3 workers
- [ ] [TASK-802] Configurer Ingress Controller avec certificats TLS
- [ ] [TASK-803] Déployer PostgreSQL avec Patroni (HA)
- [ ] [TASK-804] Configurer Redis pour cache et sessions
- [ ] [TASK-805] Setup HashiCorp Vault pour secrets
- [ ] [TASK-806] Implémenter HPA (Horizontal Pod Autoscaler)
- [ ] [TASK-807] Configurer Prometheus + Grafana
- [ ] [TASK-808] Setup ELK stack pour logs centralisés
- [ ] [TASK-809] Configurer backups automatiques (PostgreSQL + K8s)
- [ ] [TASK-810] Tests de disaster recovery

#### Epic 9: Tests et Qualité

**TODO:**
- [ ] [TASK-901] Tests unitaires backend (objectif 80% couverture)
- [ ] [TASK-902] Tests d'intégration API
- [ ] [TASK-903] Tests E2E frontend (Cypress/Playwright)
- [ ] [TASK-904] Tests de charge (K6 - 200 users simultanés)
- [ ] [TASK-905] Tests de sécurité SAST (SonarQube)
- [ ] [TASK-906] Tests de sécurité DAST (OWASP ZAP)
- [ ] [TASK-907] Audit de dépendances (Snyk)
- [ ] [TASK-908] Tests d'accessibilité RGAA

#### Epic 10: Documentation et Formation

**TODO:**
- [ ] [TASK-1001] Rédiger documentation architecture technique
- [ ] [TASK-1002] Documenter API avec Swagger/OpenAPI
- [ ] [TASK-1003] Rédiger guide d'installation et déploiement
- [ ] [TASK-1004] Rédiger manuel utilisateur avec captures d'écran
- [ ] [TASK-1005] Créer vidéos de formation (admin, logisticien, utilisateur)
- [ ] [TASK-1006] Préparer support de formation PPT
- [ ] [TASK-1007] Organiser sessions de formation (3 niveaux)