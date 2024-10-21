# ft_transcendence

![Pandapong !](./pandapong.png)


✅ Validé à 125% le 30 mai 2024

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

Ce projet consiste à créer un site web pour participer à une compétition du célèbre jeu Pong !

Ceci est le detail des modules implementes par [vfuster66](https://github.com/vfuster66), [sekhmet007](https://github.com/sekhmet007) et [idumenil](https://github.com/idumenil)

Nous avons implémenté 7 modules majeurs et 7 modules mineurs.

Nous avons tenté le module 3D, le jeu fonctionne mais nous n'avons pas eu le temps d'arriver à le connecter pour envoyer les données utilisateurs
dans le jeu et récupérer les données de jeu dans la base de données.
Nous avions également prévu d'installer la partie devops mais le temps nous  manqué également. J'ai quand même laissé la documentation de ces 3 modules dans le README, que cela puisse vous servir.

Comme tous les projets de 42, il y aurait toujours quelque chose à améliorer, à rajouter et tous le modules sont intéressants, il faut. à un moment savoir dire stop.
Si j'ai un conseil à vous donner, prenez bien le temps, de réfléchir aux modules que vous voulez implémenter, aux imbrications entre les différents modules et à la répartition entre les membres de l'équipe. Il vaut mieux perdre du temps à la préparation, vous le regagnerez lorsque vous vous mettrez à coder.

Certains ont choisi d'héberger leur site, ce qui n'a pas été notre cas, nous avons juste pris un nom de domaine et les certificats ssl afin que le site soit sécurisé, allez voir les offres du github package, vous trouverez de quoi faire l'un ou l'autre gratuitement.


<a id="summary"></a>
<hr>
<details><summary>Partie obligatoire</summary>
<br>

- [Generalites](#generalites)
- [Contraintes](#contraintes)
- [Jeu](#Jeu)
- [Securite](#securite)

</details>
<hr>

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Generalites
```
Grâce à votre site web, les utilisateurs pourront jouer à Pong entre eux.
Vous fournirez une jolie interface utilisateur et des parties en ligne multijoueurs en temps réel !

Le projet est construit en deux parties :
- Une partie obligatoire qui compte pour 25% de la note
- 7 modules majeurs a choisir parmi 16 modules majeurs et 11 modules mineurs
  > 2 modules mineurs = 1 module majeur
```
## Contraintes
```
- Site avec ou sans backend.
- Application simple-page. L’utilisateur doit pouvoir utiliser les boutons Précédent et Suivant du navigateur.
- L’utilisateur ne doit pas rencontrer d’erreurs non-gérées ou d’avertissements lorsqu’il navigue sur le site web.
- Tout le projet doit être compilé en lançant une seule ligne de commande qui démarrera un conteneur autonome
```
## Jeu
```
- Participer à une partie de Pong en temps réel contre un autre utilisateur directement sur le site web.
- Un joueur doit pouvoir jouer contre un autre joueur, mais doit aussi pouvoir organiser un tournoi.
  Ce tournoi consiste en plusieurs joueurs qui peuvent jouer les uns contre les autres.
  Vous avez la flexibilité de déterminer comment vous allez implémenter le tournoi,
  mais il doit clairement indiquer qui joue contre qui et l’ordre des joueurs.
- Un système d’inscription est requis
- Il doit y avoir un système de "matchmaking" : le système de tournoi organise le "matchmaking" des participants,
  et annonce la prochaine partie.
- Tous les joueurs respectent les mêmes règles, incluant une vitesse identique des barres (paddles).
  Ce pré-requis s’applique également lorsque vous utilisez une IA ; celle-ci doit se déplacer à la même vitesse que le joueur.
- Le jeu doit capturer l’essence du Pong original (1972).
```
## Securite
```
- Tout mot de passe stocké dans votre base de données doit être chiffré.
- Votre site web doit être protégé contre les injections SQL/XSS.
- Si vous avez un backend ou n’importe quelle autre fonctionnalité,
  il est obligatoire d’implémenter une connexion HTTPS pour tous les aspects (wss au lieu de ws...).
- Vous devez implémenter une form de validation pour les formulaires ou toute entrée utilisateur,
  que ce soit sur la page de base s’il n’y a pas de backend, ou côté serveur si un backend est utilisé.
- Pour des raisons de sécurité évidentes, les informations d’identification, clés API, variables d’environnement, etc.
  doivent être sauvegardées localement dans un fichier .env et
  ignoré par .git. Si cette notion est ignorée, il en résultera d’un échec immédiat du projet.
```
![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

<a id="summary"></a>
<hr>
<details><summary>Modules</summary>
<br>

- [Web](#web)
- [Utilisateurs](#utilisateurs)
- [IA-Algo](#ia-algo)
- [Cybersecurite](#cybersecurite)
- [Devops](#devops)
- [Graphique](#graphique)
- [Accessibilite](#accessibilite)
- [Oriente_objet](#oriente_objet)

</details>
<hr>

![-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/rainbow.png)

## Web
### Module majeur : Utiliser un framework en backend.
```
* Qu'est-ce que Django ?

Django est un framework web open-source de haut niveau, écrit en Python, qui encourage le développement
rapide et une conception propre et pragmatique. Créé en 2005, Django a été conçu pour aider les développeurs
à créer des applications web complexes et riches en fonctionnalités de manière rapide et efficace,
tout en suivant le principe DRY (Don't Repeat Yourself).

* Caractéristiques principales de Django

    - ORM (Object-Relational Mapping) :
    Django fournit un ORM puissant qui permet de manipuler les bases de données relationnelles en utilisant
    des objets Python.
    Vous pouvez créer, lire, mettre à jour et supprimer des enregistrements dans la base de données sans écrire de SQL.

    - Administration automatique :
    Django génère automatiquement une interface d'administration pour vos modèles, ce qui vous permet de
    gérer facilement les données de votre application.

    - URL routing :
    Django utilise un système de routage d'URL basé sur des expressions régulières, ce qui permet de mapper
    les URL aux vues de manière flexible.

    - Templates :
    Django utilise un moteur de templates propre qui permet de séparer la logique de l'application du design.
    Les templates Django utilisent un langage de balisage simple pour afficher dynamiquement des données.

    - Formulaires :
    Django facilite la création, la validation et le traitement des formulaires web, en incluant des
    fonctionnalités de protection contre les attaques CSRF (Cross-Site Request Forgery).

    - Authentification et autorisation :
    Django inclut un système complet de gestion des utilisateurs, des groupes, des permissions
    et des sessions.

    - Sécurité :
    Django intègre de nombreuses fonctionnalités de sécurité pour protéger vos applications contre
    les attaques courantes comme les injections SQL, les attaques XSS (Cross-Site Scripting) et CSRF.

    - Extensions et applications tierces :
    Django dispose d'un écosystème riche de bibliothèques et d'applications tierces qui étendent
    ses fonctionnalités de base, disponibles via le Python Package Index (PyPI).

* Architecture de Django

Django suit le modèle de conception MTV (Model-Template-View), qui est similaire au modèle MVC
(Model-View-Controller) mais avec des différences terminologiques :

    - Model :
    Les modèles définissent la structure des données de l'application. Ils sont représentés par des
    classes Python et sont traduits en tables de base de données par l'ORM.

    - Template :
    Les templates définissent l'apparence et la présentation des données. Ils utilisent un langage de
    balisage simple pour insérer dynamiquement des données dans les fichiers HTML.

    - View :
    Les vues contrôlent la logique de l'application et interagissent avec les modèles et les templates
    pour générer les réponses HTTP.
```
---
### Module mineur : Utiliser un framework ou toolkit en frontend.
```
* Qu'est-ce que Bootstrap ?

Bootstrap est un framework CSS open-source développé par Twitter pour aider à créer des sites web et des
applications web réactifs et modernes. Il est populaire pour sa simplicité, sa flexibilité et son large
éventail de composants préconstruits qui facilitent le développement front-end. Bootstrap inclut des styles CSS
et des composants JavaScript prêts à l'emploi qui permettent de créer des interfaces utilisateur attrayantes
et réactives.

* Caractéristiques principales de Bootstrap

    - Réactivité et conception mobile-first :
    Bootstrap est conçu pour être réactif dès le départ, ce qui signifie que les mises en page s'adaptent
    automatiquement à différentes tailles d'écran et dispositifs. La conception mobile-first signifie que les
    styles sont d'abord appliqués aux petits écrans, puis étendus aux écrans plus grands.

    - Système de grille flexible :
    Bootstrap utilise un système de grille basé sur 12 colonnes qui permet de créer facilement des mises
    en page complexes. Les grilles peuvent être imbriquées et sont réactives par défaut.

    - Composants préconstruits :
    Bootstrap inclut de nombreux composants UI tels que des boutons, des formulaires, des modales, des carrousels,
    des cartes, des barres de navigation, et bien plus encore. Ces composants sont faciles à personnaliser et
    à intégrer.

    - Utilisation de classes utilitaires :
    Bootstrap fournit une vaste collection de classes utilitaires qui permettent de modifier rapidement
    l'apparence et le comportement des éléments HTML, comme les marges, les espacements, les couleurs,
    et les typographies.

    - Thèmes et personnalisation :
    Bootstrap peut être facilement personnalisé pour s'adapter à la charte graphique de votre site.
    Vous pouvez personnaliser les variables Sass pour changer les couleurs, les polices, et
d'autres styles globaux.

    - Compatibilité avec JavaScript :
    Bootstrap inclut des plugins JavaScript qui ajoutent des fonctionnalités interactives aux composants.
    Vous pouvez utiliser les plugins JavaScript fournis par Bootstrap ou les remplacer par des
    solutions personnalisées.

* Structure de Bootstrap

Bootstrap est organisé en plusieurs parties :

    - CSS de base :
    Inclut les styles de base pour le typographie, les boutons, les formulaires, les tables, etc.

    - Système de grille :
    Un système de grille réactif qui permet de créer des mises en page flexibles.

    - Composants :
    Divers composants UI comme les barres de navigation, les cartes, les alertes, les modales, etc.

    - Classes utilitaires :
    Classes pour modifier rapidement les marges, les espacements, les couleurs, les alignements, etc.

    - JavaScript :
    Plugins JavaScript pour ajouter des fonctionnalités interactives aux composants.
```
---
### Module mineur : Utiliser une base de données en backend.
```
* Qu'est-ce que PostgreSQL ?

PostgreSQL est un système de gestion de base de données relationnelle (SGBDR) open-source, puissant et riche
en fonctionnalités. Connu pour sa robustesse, sa conformité aux normes SQL et son extensibilité, PostgreSQL
est utilisé par de nombreuses entreprises et organisations pour gérer des bases de données critiques.

* Caractéristiques principales de PostgreSQL

    - Conformité aux normes SQL :
    PostgreSQL est conforme aux standards SQL, ce qui assure une compatibilité et une interopérabilité
    maximales avec d'autres systèmes et outils.

    - Extensibilité :
    PostgreSQL permet aux utilisateurs de définir leurs propres types de données, fonctions, opérateurs,
    agrégats et méthodes d'indexation, ce qui en fait un système très flexible et adaptable.

    - Support ACID :
    PostgreSQL offre un support complet pour les transactions ACID (Atomicité, Cohérence, Isolation, Durabilité),
    garantissant l'intégrité des données même en cas de défaillance du système.

    - Types de données avancés :
    PostgreSQL prend en charge une vaste gamme de types de données, y compris les types primitifs
    (entiers, chaînes, dates), les types géométriques, les JSON, les types réseau, et les types définis par l'utilisateur.

    - Indexation puissante :
    PostgreSQL propose plusieurs types d'index (B-tree, Hash, GiST, SP-GiST, GIN, BRIN) pour optimiser les
    performances des requêtes.

    - Fonctionnalités de sécurité avancées :
    PostgreSQL offre des fonctionnalités de sécurité avancées, telles que le contrôle d'accès basé sur les rôles,
    le chiffrement SSL, et l'audit des connexions et des modifications de données.

    - Support des langages procéduraux :
    PostgreSQL prend en charge plusieurs langages procéduraux pour écrire des fonctions et des déclencheurs,
    y compris PL/pgSQL, PL/Tcl, PL/Perl, et PL/Python.
```
---
## Utilisateurs
### Module majeur : Gestion utilisateur standard, authentification, utilisateurs en tournois.
```
* Dépendances:

    - Ajouter les bibliothèques django-allauth pour la gestion des utilisateurs et l'authentification,
      ainsi que Pillow pour la gestion des avatars

* Configuration:

    - Creer l'application utilisateur dans le projet django
    - Ajouter allauth, allauth.account, et allauth.socialaccount à la liste d'applications installées
    - Ajouter django.contrib.auth.middleware.AuthenticationMiddleware et django.contrib.messages.middleware.MessageMiddleware
      aux middlewares
    - Ajouter la configuration de l'authentification dans settings.py
    - Ajouter les URL de redirection de allauth dans le fichier urls.py
    - Créer les modèles utilisateurs personnalisés
    - Mettre à jour settings.py pour utiliser le modèle utilisateur personnalisé
    - Créer des formulaires pour la mise à jour des informations utilisateurs
    - Créer des vues pour gérer les utilisateurs
    - Créer des templates pour les vues utilisateurs
    - Configurer les URL pour les vues utilisateurs
    - Gérer les avatars et les fichiers statiques, s'assurer que que MEDIA_URL et
      MEDIA_ROOT sont configurés dans settings.py
    - Ajouter des fonctionnalités pour gerer les amities
    - Ajouter des fonctionnalites pour afficher les statistiques
    - Ajouter des fonctionnalites pour afficher l'historique
```
---
### Module majeur : Implémenter une authentification à distance.
```
* Dépendances:

    - Ajoute la bibliothèque social-auth-app-django pour gérer l'authentification OAuth 2.0

* Configuration:

    - Ajouter social_django à la liste d'applications installées
    - Ajouter social_django.middleware.SocialAuthExceptionMiddleware aux middlewares
    - Configurer les paramètres d'authentification
      (identifiants OAuth 42, backends d'authentification, URL de redirection après connexion, middlewares sociaux)
    - Ajouter les URLs de redirection dans urls.py (social-django)
    - Créer une application OAuth sur la plateforme 42
       > Se connecter à son compte 42.
       > Aller dans l'espace développeur et créer une nouvelle application.
       > Renseigner les informations nécessaires comme le nom de l'application, la description,
         l'URL de redirection (qui devrait correspondre à SOCIAL_AUTH_42_REDIRECT_URI).
       > Noter le client_id et le client_secret fournis par la plateforme 42, pour configurer l'application Django.
    - Configurer les variables d'environnement
    - Créer les vues et les templates
    - Configurer la redirection après déconnexion
```
---
### Module majeur : Ajout d’un second jeu avec historique utilisateur et "match- making".
```
* Configuration

    - Créer une nouvelle application Django
    - Ajouter l'application à settings.py
    - Définir les modèles pour l'historique des parties et le matchmaking
    - Créer le front-end du jeu avec JavaScript et HTML
    - Ajouter le code JavaScript pour le jeu
    - Définir les vues pour le jeu et l'historique des parties
    - Configurer les URL pour le jeu
    - Définir les vues pour le matchmaking
    - Configurer les URL pour le matchmaking
    - Créer des templates pour le matchmaking (recherche de match, details du match, aucun adversaire disponible)
```
---
### Module majeur : Clavardage en direct (live chat).
```
* Dépendances:

    - Ajouter les bibliothèques Django Channels et Redis

* Configuration:

    - Creer l'application de chat dans le projet django
    - Ajouter channels et l'application de chat à la liste d'applications installées
    - Ajouter la configuration de Channels et de Redis dans settings.py
    - Créer ou modifier le fichier asgi.py dans le répertoire du projet
      pour inclure la configuration de Channels
    - Définir les modèles pour les messages, les blocs et les invitations de jeu dans chat/models.py
    - Définir les URL pour les WebSocket dans chat/routing.py
    - Implémenter les consommateurs pour gérer les connexions WebSocket dans chat/consumers.py
    - Créer des vues pour gérer les interactions utilisateurs
    - Créer les templates pour les vues de chat
    - Configurer les URL pour les vues de chat
```
---
## IA-Algo
### Module majeur : Implémenter un adversaire contrôlé par IA.
```
* Configuration:

    - Définir un modèle pour l'IA dans models.py
    - Développer la logique de l'IA
        > Créer un script C# pour contrôler l'IA
        > Assigner le script AIController à l'objet raquette de l'IA
    - Simuler des entrées au clavier pour l'IA
        > Modifier le script AIController pour simuler des entrées au clavier
    - Intégrer l'IA dans le système de matchmaking
        > Modifier la vue pour inclure l'option de jouer contre l'IA
        > Configurer les URL pour inclure le matchmaking avec l'IA
    - Créer des templates pour le matchmaking avec l'IA (matchmaking avec IA, match avec IA
```
---
## Cybersecurite
### Module mineur : Options de conformité au RGPD avec anonymisation des utilisateurs, gestion des données locales et suppression de comptes.
```
* Qu'est-ce que le RGPD ?

Le Règlement Général sur la Protection des Données (RGPD) est une réglementation de l'Union Européenne
qui vise à protéger les données personnelles des individus. Entré en vigueur le 25 mai 2018, le RGPD
impose des règles strictes aux organisations pour le traitement et la gestion des données personnelles,
garantissant ainsi les droits des individus en matière de protection des données.

* Principes fondamentaux du RGPD

    - Licéité, loyauté et transparence :
      Les données doivent être traitées de manière licite, loyale et transparente. Les utilisateurs doivent
      être informés de la manière dont leurs données sont collectées et   utilisées.

    - Limitation des finalités :
      Les données doivent être collectées à des fins déterminées, explicites et légitimes et ne doivent pas être
      utilisées ultérieurement de manière incompatible avec ces finalités.

    - Minimisation des données :
      Les données collectées doivent être adéquates, pertinentes et limitées à ce qui est nécessaire au regard des
      finalités pour lesquelles elles sont traitées.

    - Exactitude :
      Les données doivent être exactes et tenues à jour. Les utilisateurs doivent pouvoir corriger leurs données inexactes.

    - Limitation de la conservation :
      Les données doivent être conservées pendant une durée n'excédant pas celle nécessaire pour les
      finalités pour lesquelles elles sont traitées.

    - Intégrité et confidentialité :
      Les données doivent être traitées de manière à garantir une sécurité appropriée, y compris la protection contre
      le traitement non autorisé ou illicite et contre la perte, la destruction ou les dégâts accidentels.

    - Responsabilité :
      Les organisations doivent être en mesure de démontrer leur conformité aux principes du RGPD.

* Droits des utilisateurs sous le RGPD

    - Droit d'accès :
      Les utilisateurs peuvent demander l'accès à leurs données personnelles détenues par une organisation.

    - Droit de rectification :
      Les utilisateurs peuvent demander la correction de leurs données personnelles inexactes ou incomplètes.

    - Droit à l'effacement (droit à l'oubli) :
      Les utilisateurs peuvent demander l'effacement de leurs données personnelles sous certaines conditions.

    - Droit à la limitation du traitement :
      Les utilisateurs peuvent demander la limitation du traitement de leurs données sous certaines conditions.

    - Droit à la portabilité des données :
      Les utilisateurs peuvent recevoir leurs données personnelles dans un format structuré, couramment utilisé
      et lisible par machine, et les transmettre à un autre responsable du traitement.

    - Droit d'opposition :
      Les utilisateurs peuvent s'opposer au traitement de leurs données personnelles sous certaines conditions.

    - Droits relatifs à la prise de décision automatisée et au profilage :
      Les utilisateurs peuvent s'opposer à la prise de décisions fondées uniquement sur un traitement automatisé,
      y compris le profilage.

* Configuration:

    - Ajouter des champs pour marquer les utilisateurs comme anonymisés et pour gérer les demandes de suppression de compte.
    - Créer des formulaires pour la gestion des données personnelles
    - Créer des vues pour gérer les demandes des utilisateurs
    - Créer des templates pour les vues
    - Configurer les URL pour les vues
    - Ajouter la gestion de la desactivation, de l'anonymisation et de la suppression des comptes
    - Expliquer les droits des utilisateurs, au moment de l'inscription
```
---
### Module majeur : Implémenter l’authentification à 2 facteurs (2FA) et JWT (JSON Web Tokens).
```
* Dépendances:

    - Ajouter les bibliothèques django-otp, django-two-factor-auth et djangorestframework-simplejwt

* Configuration:

    - Ajouter django_otp et two_factor à la liste des applications installées,
      ainsi que les applications REST framework et JWT
    - Ajouter django.middleware.security.SecurityMiddleware et django_otp.middleware.OTPMiddleware
      aux middlewares
    - Ajouter la configuration pour le REST framework et JWT dans settings.py
    - Ajouter les URLs nécessaires pour 2FA et JWT dans votre fichier urls.py
    - Créer les vues pour l'activation du 2FA
    - Créer les templates pour le 2FA
    - Configurer les URLs pour les vues
    - Configurer l'authentification avec JWT
    - Configurer les permissions et la sécurité
```
---
## Devops
### Module majeur : Configuration de l’infrastructure pour la gestion des journaux (logs).
```
* Qu'est-ce que ELK?

Ce module vise à déployer Elasticsearch pour le stockage des journaux, configurer Logstash pour la collecte
et le traitement des journaux, et utiliser Kibana pour la visualisation des données. Cette infrastructure
permet de stocker, traiter, et visualiser efficacement les journaux, tout en assurant la sécurité et la gestion
efficace des données. Les politiques de rétention et d’archivage des données garantissent également une gestion o
ptimale du stockage des journaux

* Configuration:

    - Mettre a jour docker-compose
    - Créer le répertoire logstash-pipeline
    - Créer un fichier de configuration pour Logstash
    - Configurer Filebeat pour envoyer les journaux à Logstash
        > Créer un fichier de configuration Filebeat
        > Déployer Filebeat avec Docker
    - Ou récupérer les logs grâce au logger de Django
    - Configurer Kibana
        > Accéder à Kibana
        > Configurer l'index pattern
    - Créer des tableaux de bord dans Kibana
        > Accéder à Discover
        > Créer des visualisations
        > Créer un tableau de bord
    - Définir des politiques de rétention et d’archivage des données
        > Configurer la gestion du cycle de vie des index (ILM)
        > Appliquer la politique aux index de journaux
    - Mettre en place des mesures de sécurité
        > Configurer l'authentification et l'autorisation
        > Configurer TLS/SSL pour Elasticsearch, Logstash, et Kibana
```
---
### Module mineur : Système de monitoring.
```
* Qu'est-ce que Prometheus?

Prometheus est un système de surveillance open-source qui recueille et stocke des métriques sous forme de séries
temporelles (c'est-à-dire des informations avec des horodatages). Il a été développé à l'origine par SoundCloud
et fait maintenant partie de la Cloud Native Computing Foundation (CNCF).

* Principales fonctionnalités de Prometheus

    - Collecte de métriques :
        Prometheus utilise un modèle de scraping, où il extrait périodiquement les métriques de points finaux spécifiés (endpoints) appelés exporters.
        Les exporters sont des services qui exposent des métriques au format que Prometheus peut lire.

    - Stockage de données :
        Les métriques sont stockées sous forme de séries temporelles, identifiées par un nom et une série de paires clé-valeur.
        Prometheus dispose de sa propre base de données de séries temporelles pour stocker les données.

    - Langage de requête PromQL :
        Prometheus offre un langage de requête puissant, PromQL, pour interroger et extraire des données de métriques.
        PromQL permet des opérations mathématiques, des agrégations et des jointures sur les données de séries temporelles.

    - Alerting :
        Prometheus permet de définir des règles d'alerte basées sur les requêtes PromQL.
        Les alertes peuvent être envoyées à divers systèmes de notification via Alertmanager, un composant de Prometheus.

    - Visualisation et tableaux de bord :
        Prometheus peut s'intégrer à Grafana pour la visualisation des métriques via des tableaux de bord interactifs.

* Cas d'utilisation

    Surveillance des performances des applications et des infrastructures.
    Suivi des métriques d'utilisation des ressources (CPU, mémoire, etc.).
    Surveillance des applications distribuées et des microservices.

* Qu'est-ce que Grafana?

Grafana est une plateforme open-source pour la surveillance et la visualisation des données métriques. Elle permet de créer
des tableaux de bord interactifs et des graphiques à partir de diverses sources de données, y compris Prometheus.

* Principales fonctionnalités de Grafana

    - Sources de données multiples :
        Grafana supporte de nombreuses sources de données, telles que Prometheus, Elasticsearch, InfluxDB, MySQL, PostgreSQL,
        et bien d'autres.
        Chaque source de données peut être configurée individuellement pour récupérer et afficher les données.

    - Tableaux de bord interactifs :
        Les utilisateurs peuvent créer des tableaux de bord personnalisés avec des graphiques, des jauges, des cartes thermiques
        et d'autres types de visualisations.
        Les tableaux de bord peuvent être partagés et exportés.

    - Alerting :
        Grafana offre des fonctionnalités d'alerte intégrées qui permettent de configurer des notifications basées sur
        les conditions définies dans les graphiques.
        Les alertes peuvent être envoyées via email, Slack, PagerDuty, et d'autres canaux.

    - Plugins et extensions :
        Grafana a une architecture de plugins qui permet d'étendre ses fonctionnalités avec des plugins développés par la
        communauté ou par Grafana Labs.
        Il existe des plugins pour des sources de données supplémentaires, des types de visualisations personnalisées, et
        des intégrations avec d'autres outils.

    - Authentification et sécurité :
        Grafana supporte l'authentification par mot de passe, OAuth, LDAP, et d'autres méthodes.
        Des permissions granulaires peuvent être définies pour contrôler l'accès aux tableaux de bord et aux sources de données.

* Cas d'utilisation

    Création de tableaux de bord de surveillance en temps réel.
    Analyse des performances des applications et des infrastructures.
    Visualisation des données historiques pour le dépannage et l'optimisation.
    Configuration d'alertes pour la détection proactive des problèmes.

* Configuration :

    - Déployer Prometheus
        > Configuration de Docker Compose
        > Créer un fichier de configuration pour Prometheus
    - Configurer des exportateurs pour capturer des métriques (Node Exporter)
        > Ajouter Node Exporter au docker-compose
        > Ajouter Node Exporter au fichier de configuration de Prometheus
    - Configurer Grafana
        > Accéder à Grafana
        > Configurer la source de données Prometheus
    - Créer des tableaux de bord dans Grafana
        > Créer un nouveau tableau de bord
        > Configurer les panels
        > Enregistrer le tableau de bord
    - Configurer des règles d’alerte dans Prometheus
        > Ajouter des règles d'alerte à la configuration de Prometheus
        > Créer le fichier alert.rules
        > Redémarrer Prometheus pour appliquer les changements
    - Configurer la rétention et le stockage des données
    - Mettre en place des mécanismes d'authentification pour Grafana
```
---
## Graphique
### Module majeur : Utilisation de techniques avancées 3D.
```
Jeu réalisé sur Unity en c# puis exporté en format WebGL.
Le jeu est géré en local, les joueurs joue sur le même clavier.
Les tournois sont a élimination direct.

* Pong3D:

 -> On dois gérer la communication entre Django et le jeu pong3d exporter en WebGL.
La communication doit se faire dans les deux sens donc il faudra gérer les méthodes Get et Post en entre le Django et le jeu. Afin de récupère les alias, avatar, les scores de chaque joueurs et les vainqueurs.
Le jeu n’interagît pas directement avec la base de données PostgreSQL on le fait à travers Django.

-> le jeu Pong3D en détaille ci-joint

->On quitte le jeu Pong3D, pour retourner sur le menu des jeux de la pages web


* Fonctionnement détailler du jeu Pong3D:

On demarre sur le Menu (scene MainMenu)
Selection du jeu par 4 boutons : 
Gamer Vs AI
Gamer VS Gamer
Tournament
Quit

* Gamer Vs AI :

	- Récupération de l’alias du joueur et de son avatar:
		-> Django vers jeu en WebGL
	- Lancement de la scène Gamer Vs AI.
	- récupérer le score du joueur en fin de partie pour l’intégrer à sa page de profile ou ses statique de jeu sont visible.
		-> Jeu en WebGL vers Django vers Frontend.

	- Scène gagne ou perdu.
	- Reviens au Menu (scène MainMenu).

* Gamer Vs Gamer :

	- Sélections des deux joueurs.
		-> Django vers jeu : afficher la liste des joueurs connecté. 
	- Récupérations des Alias et des avatars des deux joueurs.
		-> Django vers jeu
	- Lancement de la scène Gamer Vs Gamer.
	- récupérer les scores de chaque joueurs pour les intégrer a leur pages de profiles respective.
		-> Jeu vers Django vers Frontend.
	- scène perdant / gagnant.
	- retour sur scène Menu (MainMenu).

* Tournament : (en 4 match à élimination direct)
 
Scène Tournamentsetup : choix des joueurs ou machmaking, par 2 boutons.
	- Sélections des joueurs ou sélection par matchmaking.
		-> Django vers jeu : afficher la liste des joueurs connecté.
	- Récupérations des Alias et des avatars des deux joueurs.
		-> Django vers jeu
	- Lancement de la scène Tournament_1match :
		- la scène Tournament_1match sera lancé 4 fois et a chaque fin de match de la scène Tounament_1match on doit récupérer : 
				- le vainqueur de chaque match.
				- le score du chaque joueur du match.
		-> jeu vers Django.
Attention : chaque vainqueur doit être sélectionné pour la scène suivante Tournament_demi-final.
	-Scène Looser/winner ou winner/Looser a la fin de chaque match.

	- Récupérations des gagnants des précédents match et de leur alias et avatar.
		-> django vers le jeu. (Re matchmaking)
	- lancement de la scène tournament_demi-final 2 fois de suite avec les vainqueurs uniquement de la scène précédente tournament_1match.
	- a chaque fin de match de la scène Tounament_demi-final on doit récupérer : 
				- le vainqueur de chaque match.
				- le score du chaque joueur du match.
		-> jeu vers django.
Attention : chaque vainqueur doit être sélectionné pour la scène suivante Tournament_final.

	- Lancement de la scène Tournament final avec les deux denier joueurs restant.
	- a la fin de la partie on recupère le noms du vainqueur et le scores de chaque joueurs.
		-> jeu vers Django.
	- scène du vainqueur.
	- retour a la scène du Menu.

* Configuration avec ThreeJS:

    - Configurer le projet avec Three.js
        > Créer un nouveau projet et initialiser npm
        > Installer three, webpack webpack-cli --save-dev, babel-loader @babel/core @babel/preset-env --save-dev
        > Configurer Webpack et Babel (créer un fichier webpack.config.js, créer un fichier Babel .babelrc)
        > Créer la structure des répertoires du projet
    - Développer le jeu Pong en 3D avec Three.js
        > Initialiser la scène, la caméra et le renderer
        > Ajouter les raquettes et la balle
        > Ajouter le mouvement de la balle
        > Ajouter le contrôle des raquettes
    - Intégrer le jeu avec une interface web
        > Créer un fichier index.html dans le répertoire dist
    - Ajouter des scripts dans package.json pour démarrer le projet
    - Démarrer le projet
    - Améliorer les graphismes et la jouabilité
        > Ajouter des textures aux raquettes et à la balle
        > Ajouter des effets de post-traitement
    - Intégrer l'API pour gérer les états de jeu côté serveur
        > Ajouter les appels API pour mettre à jour les états de jeu
    - Intégration dans le projet django
        > Ajouter les fichiers Three.js dans le repertoire static
        > Créer une vue et un template pour le jeu
        > Ajouter l'URL pour la vue du jeu

* Configuration avec Unity:

    - Créer un nouveau projet Unity
    - Créer la scène principale
        > Supprimer les objets par défaut
        > Ajouter une nouvelle caméra
        > Ajouter une lumière
    - Créer les objets du jeu
        > Créer les raquettes
        > Créer la balle
    - Ajouter des scripts pour la jouabilité
        > Créer un script C# pour contrôler les raquettes
        > Éditer le script PaddleController
        > Assigner le script aux raquettes
        > Configurer les axes d'entrée
        > Créer un script C# pour contrôler la balle
        > Éditer le script BallController
        > Assigner le script à la balle
    - Ajouter des effets visuels avancés
        > Ajouter des matériaux
        > Ajouter des lumières dynamiques
        > Activer les ombres
    - Intégrer le jeu avec une interface web
        > Configurer les fichiers HTML pour la build WebGL
    - Développer des techniques avancées
        > Utiliser Shader Graph pour créer des shaders personnalisés
        > Ajouter des effets de post-traitement
    - Intégration dans le projet django
        > Ajouter les fichiers Three.js dans le repertoire static
        > Créer une vue et un template pour le jeu
        > Ajouter l'URL pour la vue du jeu
```
---
## Accessibilite
### Module mineur : Étendre la compatibilité des navigateurs web.
```
* Configuration:

    - Identifier le navigateur supplémentaire
    - Utiliser des outils de développement pour tester la compatibilité (inspecteur du navigateur)
    - Ajouter des préfixes CSS pour la compatibilité (Autoprefixer)
```
---
### Module mineur : Support de multiple langues.
```
* Configuration:

    - Ajouter les langues que l'on souhaite supporter dans settings.py
    - Configurer les chemins de localisation dans settings.py
    - Ajouter django.middleware.locale.LocaleMiddleware aux middlewares
    - Utiliser les fonctions de traduction de Django pour marquer les chaînes de caractères qui
      doivent être traduites dans vos templates et vos fichiers Python (trans, gettext)
    - Utiliser les commandes de gestion de Django pour créer des fichiers de traduction pour chaque langue supportée
    - Remplir les fichiers de traduction générés avec les traductions appropriées.
    - Compiler les fichiers de traduction
    - Ajouter un formulaire de sélection de langue dans les templates pour permettre
      aux utilisateurs de changer la langue d'affichage.
    - Ajouter la gestion de la langue dans les URLs
```
---
## Oriente objet
### Module majeur : Remplacer le Pong de base par un Pong côté serveur et implémentation d’une API.
```
* Configuration:

    - Développer la logique côté serveur pour le jeu Pong
        > Créer une nouvelle application Django
        > Ajouter l'application à la liste des applications installees
        > Créer les modèles nécessaires pour le jeu
    - Créer l’API pour le jeu Pong
        > Créer des serializers pour les modèles
        > Créer des vues pour gérer les points d'accès de l'API
        > Configurer les URL pour l’API
    - Développer la logique de jeu côté serveur
        > Modifier les vues pour inclure la logique de jeu
    - Intégrer le jeu Pong côté serveur avec l’application web
        > Créer une vue pour afficher le jeu
        > Ajouter les URL pour les templates
        > Créer le template HTML pour le jeu
    - Intégrer le jeu Pong côté serveur avec une interface CLI
        > Ajouter des commandes de gestion pour interagir avec le jeu via CLI
        > Ajouter une commande pour déplacer la balle
```
---
