# Installation et routine — Session reference zones

## Installation

1. Ouvrir un graphique standard NQ/MNQ, puis Pine Editor. Copier **tout** `key_zones.pine`, sauvegarder et ajouter au graphique.
2. Vérifier la compilation dans TradingView. Elle n'a pas pu être exécutée dans l'environnement de livraison ; ne pas considérer la revue documentaire comme un résultat du compilateur.
3. Utiliser des chandeliers standard 1, 5, 10, 15, 60 ou 240 minutes et la session étendue. Sur NQ1!, le tableau doit indiquer le contrat daté courant ; sinon le sélectionner dans Source contract. En replay, sélectionner le contrat qui correspond à la période étudiée.
4. Garder 100 000 minutes demandées et au moins 20 sessions cash complètes pour le warmup. Le plan ou le flux peut fournir moins. Des lignes absentes avec état Warmup sont une absence de données, pas une raison de réduire arbitrairement le lookback.
5. Contrôler les droits temps réel CME : le plan TradingView et l'abonnement de marché sont distincts. Pour la conversion seulement, contrôler aussi les données index/ETF. Sans données synchronisées, utiliser des coordonnées natives vérifiées.

## Réglages de départ

Conserver les mêmes paramètres de calcul sur toutes les périodes. RS, 20 observations, OR 30 minutes, demi-largeur 0,015 sigma, fusion 0,03, plafond complet 0,08, distance 3 sigma sont des réglages initiaux non calibrés.

| Graphique | Densité conseillée après réception | Calculs |
|---|---|---|
| 1m | 6–8 zones, labels Small, alertes facultatives après test | Source 1m identique |
| 5m | 8 zones, labels Small | Identiques |
| 10m | 8 zones | Identiques |
| 15m | 6–8 zones | Identiques |
| 1h | 4–6 zones, masquer OR via son masque si encombrant | OR reste calculé sur 1m |
| 4h | 4 zones, labels Tiny/Small, carte actuelle seulement | Même source et même warmup |

Les défauts du script affichent toutes les familles sur les six périodes. Pour les masques, utiliser `1,5,10,15,60,240` ; 1h se note 60 et 4h 240. La visibilité ne change pas les centres/largeurs/compte d'une zone commune. Désactiver un interrupteur de famille, en revanche, l'enlève du modèle sur toutes les périodes.

## Routine quotidienne courte

- Vérifier contrat daté, heure source, warmup et calendrier. Le calendrier cash par défaut couvre **2026 seulement**. Mettre à jour les dates de l'année et les horaires futures spécifiques à CME.
- Ajouter les annonces à partir de BLS/BEA/Fed/ISM et des relations investisseurs des entreprises, en **heure New York** : `YYYYMMDD-HHMM`. Exemple vérifié à la date du dossier : `20261029-0830;20261106-0830;20261110-0830`. Recontrôler avant la séance : le script ne met pas ce calendrier à jour.
- Si vous disposez d'un fournisseur d'options transparent, enregistrer hors du script la définition du niveau, le fournisseur, le timestamp, le sous-jacent et l'univers d'échéances. Sans source fiable, laisser Levels vide et gamma Unknown.
- Coller `CW:prix;PW:prix;ZG:prix;PIN:prix`. Exemple **fictif, pas des niveaux actuels** : `CW:25000;PW:24500;ZG:24750`. Chaque prix doit employer le même sous-jacent sélectionné. Aucun séparateur de milliers.
- Sélectionner Native pour NQ/ES ; NDX / index ou QQQ / ETF pour la conversion. Pour ES/MES, les défauts NDX/QQQ ne conviennent pas : choisir SPX/SPY ou rester Native.
- Vérifier l'heure de conversion. Le défaut fige la première minute cash synchronisée. Après 24 heures sans nouveau couple synchronisé, les niveaux convertis disparaissent ; un prix natif vérifié est préférable à une conversion périmée.
- Regarder le nombre de familles et la largeur réelle, puis le budget de perte encore disponible. L'indicateur ne fournit ni entrée automatique ni stop garanti.

## Calendriers

Cash close overrides : `YYYYMMDD=HHMM`, `0000`=fermé, `1300`=clôture 13:00 New York. Le calendrier Nasdaq 2026 est préchargé ; les autres années doivent être renseignées.

Futures close overrides : même syntaxe, horaires spécifiques au produit CME. L'override s'applique jusqu'à l'ouverture Globex suivante. Le calendrier cash ne remplace pas ce calendrier futures. Les sessions sont des plages simples ; conserver une référence cash intrajournalière et une ouverture Globex après celle-ci.

Pour afficher des références actuelles sur NQ1!, l'historique demandé est celui du contrat daté courant, pas l'ancien front. Après changement de contrat, recharger et vérifier la source. Pour étudier une ancienne semaine de roll, passer au bon contrat daté explicitement. Aucune détection heuristique d'un roll à partir d'un gap n'est utilisée.

## Alertes

Activer Enable entry alerts, puis créer une alerte TradingView sur **Any alert() function call**. Le script ne crée pas lui-même une alerte serveur. Les contacts utilisent la zone connue sur le snapshot précédent, sont constatés après clôture minute, puis notifiés avec le délai du flux/source. Ils ne constituent pas un ordre au prix de contact.

Par défaut : 2 familles, cooldown global 10 minutes, âge source maximum 4 minutes, silence dans les fenêtres d'événements. Recréer l'alerte après modification du code, des inputs, de la période ou du contrat : TradingView conserve sa propre copie de ces réglages.

## Réception TradingView à effectuer

| Cas | Résultat à vérifier |
|---|---|
| Compilation v6 | Zéro erreur et absence de runtime error avec les réglages valides. |
| Six graphiques | À heure Source NY identique, mêmes centres/bornes/sigma après warmup et mêmes familles de calcul. |
| 09:30 NY | ON figé, VW commence, OR absent. Pas de valeur OR finale sur les premières minutes. |
| 10:00 NY, OR30 | Publication des bornes OR seulement après complétion et délai source. |
| Clôture cash | Nouveaux PDH/PDL/PCC/PVW/sigma après session complète ; pas de mélange avec un close de 17:00. |
| 17:00–18:00 | Aucun accumulateur ne prend des barres de maintenance ; conservation d'affichage si tableau temporairement vide. |
| Dates DST | NY conserve 09:30 ; Paris peut afficher 14:30 ou 15:30 selon les semaines. |
| Jour cash fermé | Aucun faux cash open/VWAP créé depuis les futures. |
| Early close | Compteur de session adapté ; dernière minute attendue validée. |
| Historique amputé | Premières sessions incomplètes ignorées, warmup explicite, aucun index de tableau hors borne. |
| Volume absent | VW/PVW indisponibles ; pas de moyenne de remplacement silencieuse. |
| Conversion hors cash | Couple ratio/base figé ; aucune poursuite artificielle de NQ avec un NDX périmé. |
| Roll | Source datée correcte, pas de niveaux venant d'une ancienne échéance ; recréer les alertes. |
| Temps réel 1m/4h | Observer plusieurs minutes, puis recharger ; comparer valeurs et heures. Mesurer délai réel et absence de doublons. |
| Charge maximale | 24 zones, 12 niveaux manuels, 100k minutes ; pas de dépassement de temps/mémoire. |

Conserver captures et timestamps pour les échecs. Une erreur compilateur doit être corrigée à la racine dans le fichier complet ; les tests Python ne démontrent pas la compilation Pine.

## Validation locale optionnelle

Depuis le dépôt : `python3 -m unittest discover -s validation -v`. Les données de ces tests sont synthétiques.

Le protocole empirique et la CLI sont documentés dans `validation/README.md`. Il faut vos propres minutes de contrats datés et un journal causal de zones, pas des captures de la carte actuelle. Séparer les métriques de contact, de réaction et de PnL. Les paramètres et coûts de l'exemple CLI illustrent la syntaxe, sans prétendre être calibrés NQ.
