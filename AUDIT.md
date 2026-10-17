# Session reference zones — note de recherche et audit de v1

Date de vérification : **17 octobre 2026**, Europe/Paris. Marché : NQ/MNQ, adaptation ES/MES. Fichier livré : `key_zones.pine`, Pine Script v6.

## Résultat et limites de validation

Le programme produit une carte de références explicables, pas une estimation démontrée des probabilités de retournement de NQ. Les sources ouvertes étayent des mécanismes de couverture, d'exécution et de formation des prix. Elles ne permettent pas d'affirmer qu'un contact avec nos zones bat des niveaux témoins, après coûts, sur NQ. Aucun taux de réussite, rendement ou Sharpe de marché n'est revendiqué.

Le code est complet, relu contre la documentation officielle et soumis à deux relectures indépendantes. Les formules et le banc d'essai externe ont des contrôles numériques reproductibles. **Aucun compilateur Pine ni flux TradingView n'est disponible dans cet environnement : compilation, affichage et alertes sur les six périodes restent des critères de réception à réaliser dans TradingView.** Ce livrable ne doit donc pas être présenté comme une version dont l'exécution TradingView a été certifiée. Le protocole de réception figure dans `GUIDE.md`.

La note principale décrit le code final. Les annexes reproduisent les recherches vérifiées, avec bibliographies complètes, liens, périmètre exact de lecture (texte intégral, résumé ou métadonnées) et exclusions. Une proposition exploratoire dans une annexe n'est pas une fonctionnalité du code : les définitions ci-dessous font autorité pour v1.

## 1. Architecture et informations disponibles

Un moteur unique fonctionne sur des bougies **1 minute**, indépendamment de la période d'affichage. `request.security_lower_tf` retourne des objets `Snapshot`. Le calcul est entièrement réalisé dans le contexte source ; le graphique ne reconstruit pas un opening range à partir de ses propres bougies. La documentation actuelle accepte une période demandée inférieure **ou égale** à celle du graphique, y compris le cas graphique 1m/source 1m.

Chaque champ temporel/prix du snapshot est décalé d'une minute source (`[1]`). La minute en formation n'est donc pas utilisée. Le code conserve le dernier état connu si le tableau intrabar est temporairement vide. La livraison peut être retardée d'une minute supplémentaire selon la disponibilité effective des intrabars, puis par l'arrivée d'un tick ; ce délai doit être mesuré dans TradingView. Ce choix privilégie des références confirmées plutôt qu'une notification au tick du contact.

L'identité entre graphiques signifie : **même contrat source, mêmes réglages, même minute source affichée, même historique utile et warmup complet ⇒ mêmes valeurs et mêmes zones**. Comparer seulement les heures d'ouverture de deux bougies de tailles différentes n'est pas un test d'identité. Les masques de visibilité par période sont appliqués après la fusion et le comptage des familles ; cacher une famille sur 4h ne recalcule pas les bornes de la zone commune. Les interrupteurs de calcul, eux, modifient le modèle sur toutes les périodes.

Les niveaux de la veille et le VWAP précédent proviennent de la dernière session cash entièrement observée. Les extrêmes overnight sont publiés après sa clôture à l'ouverture cash. Les bornes OR sont publiées après les 30 premières minutes, sans projeter leur valeur finale sur les premières minutes. Le VWAP courant est explicitement évolutif. La carte dessine seulement les zones actuelles ; son extension à gauche n'est pas un historique de signaux disponibles à cette époque.

## 2. Méthodes retenues et grades de preuve

Les grades concernent une proposition précise : **fort** = résultat empirique répliqué et évalué par les pairs ; **modéré** = étude isolée, modèle documenté ou recherche professionnelle transparente ; **faible** = hypothèse heuristique. Une spécification CME est une autorité contractuelle, pas une preuve de rentabilité. Une identité mathématique n'a pas besoin d'un taux de réussite empirique ; son usage pour prévoir un rebond, oui. Aucune famille de cette v1 ne mérite le grade fort pour un avantage de réaction NQ.

| Composant | Mécanisme et utilité | Preuve d'un rebond NQ | Données et échecs |
|---|---|---|---|
| PDH/PDL/PCC | Prix extrêmes et clôture cash précédents ; repères publics d'inventaire et de PnL. Aucune obligation de transaction au prix exact. | Faible ; études FX d'Osler non transférables directement. | Minutes du même contrat ; une tendance ou une information nouvelle peut traverser sans réaction. |
| ONH/ONL | Bornes du prix observé pendant la session nocturne ; contexte du risque acquis avant le cash. | Faible. | Nuit complète requise ; ni carnet d'ordres ni stops observés. |
| ORH/ORL | Résumé fixe de la découverte de prix initiale. Sert à distinguer observation établie et mouvement nouveau. | Faible ; momentum intraday ETF n'implique pas rebond sur OR. | Minutes depuis l'ouverture ; faux départs, annonces et choix arbitraire de durée. |
| VW/PVW | Benchmark économique d'exécution ; stratégies d'exécution évaluées contre le VWAP. | Modéré pour le benchmark, faible pour le retour NQ vers celui-ci. | Approximation HLC3×volume, pas VWAP exact de transactions. Aucun défenseur obligé du VWAP. |
| CW/PW/ZG/PIN manuels | Repères d'un modèle externe d'options ou d'une hypothèse de pinning. | Modéré pour certains mécanismes/études hors NQ ; faible pour ces coordonnées NQ. | Inventaire dealer inconnu, définition fournisseur et heures/échéances indispensables. |
| Volatilité de sessions terminées | Unité de distance et de largeur ; formules de diffusion documentées. | Aucune preuve d'un rebond sur ±sigma. | Gaps, sauts, annonces et échantillonnage fragilisent toute couverture probabiliste. |
| Efficacité du chemin | Description de la directionnalité, réduction de l'emphase sur VWAP. | Faible ; aucun modèle de régime estimé. | Seuils heuristiques, dépendance au pas 1m et à l'heure. |

### Références de séance et disponibilité

Pour une session cash S : `PDH=max(H_i)`, `PDL=min(L_i)`, `PCC=C_dernier`, minutes incluses entre 09:30 et 16:00 New York, clôture exclusive. PCC est donc normalement le close de 15:59, pas le dernier cours Globex et **pas le settlement CME**.

La session doit démarrer sur sa première minute attendue, ne manquer aucune minute interne et finir exactement à la dernière minute attendue ; son nombre de minutes doit également correspondre au calendrier ajusté. Une session partielle ne fournit pas de nouveaux PDH/PDL/PCC ni d'observation de variance. Le code efface ces références après une clôture incomplète plutôt que de présenter une vieille session comme « hier ». Les zéros de volume ne rendent pas invalides les prix ; l'absence de volume rend le VWAP indisponible.

`ONH=max(H_i)`, `ONL=min(L_i)` entre l'ouverture Globex 18:00 et l'ouverture cash suivante 09:30. La nuit doit inclure son début et la minute précédant le cash ; une rupture de continuité invalide les bornes. Elles restent fixes après publication et sont effacées au prochain début de session Globex. La tranche 16:00–17:00 n'est pas incluse dans cette définition overnight.

`ORH=max(H_i)` et `ORL=min(L_i)` sur les `openingMinutes` premières minutes cash, défaut 30. Le choix 30 est un compromis descriptif usuel, sans optimum statistique revendiqué. Modifier la durée définit une nouvelle hypothèse qui doit être testée séparément. Les valeurs ne sont pas publiées tant que la plage n'est pas terminée. Le fuseau du graphique n'intervient jamais.

### VWAP

Le VWAP exact est `Σp_j q_j / Σq_j` sur les transactions. V1 utilise `x_i=(H_i+L_i+C_i)/3`, `VW_t=Σv_i x_i / Σv_i` sur les minutes cash clôturées. Un volume nul contribue zéro ; une valeur `na` ou négative invalide le VWAP de toute cette session. Un total nul n'entraîne aucune division. PVW est cette même approximation sur la dernière session complète.

Guéant–Royer, Kato et Busseti–Boyd justifient le rôle de benchmark sous leurs modèles d'exécution. Ils ne justifient ni un achat automatique sous VWAP ni une obligation de retour. En journée directionnelle, le VWAP peut rester éloigné du prix et continuer à se déplacer. Il est traité comme une référence développée, non comme une ligne immuable. Aucune bande de dispersion VWAP n'est ajoutée : elle ne serait pas une bande de probabilité de rendement futur.

### Échelle de volatilité

Pour chaque session cash terminée, O,H,L,C sont construits à partir des minutes complètes du contrat source. Trois estimateurs au choix :

`v_RS = ln(H/O)ln(H/C) + ln(L/O)ln(L/C)` ;

`v_P = [ln(H/L)]² / [4 ln(2)]` ;

`v_CC = [ln(C/C_précédent)]²`.

La variance utilisée est la **moyenne arithmétique des L dernières observations valides**, `L=20`, et `sigma_points=C_dernière_session × sqrt(mean(v))`. Ce n'est ni une EWMA ni un HAR. La fenêtre finie supprime la dépendance persistante à l'initialisation d'une EWMA lorsque les graphiques chargent des historiques différents. Il faut L observations complètes ; pour clôture/clôture, L+1 sessions sont nécessaires après remise à zéro. Le facteur de conversion en points est une approximation locale du rendement logarithmique, pas une transformation lognormale exacte.

RS est le défaut parce qu'il tolère un drift constant dans le modèle de diffusion ; il ne « corrige » ni les annonces ni les sauts. Parkinson suppose notamment un drift nul. RS/Parkinson excluent le gap entre clôture et ouverture : cette échelle est une volatilité **interne à la session cash**, également utilisée comme unité pratique hors cash, sans prétendre mesurer tout le risque overnight. CC incorpore les changements de clôture à clôture mais reste une mesure quadratique sans retrait explicite de la moyenne. Des sessions manquantes ne sont pas imputées : les L observations retenues peuvent couvrir plus de L jours de calendrier.

`Open ± sigma` dans le tableau est une référence d'amplitude en points, arrondie au tick. Ce n'est pas l'espérance du high–low, un quantile estimé, une promesse de couverture de 68 %, ni une nouvelle famille de support/résistance. VXN n'est pas une dépendance du script ; son rôle contextuel et les différences implicite/réalisée sont étudiés en annexe.

### Zones et regroupement

Chaque centre brut est arrondi au tick du **contrat source**. Pour le centre arrondi p et tick δ :

`w=max(δ,0.015 sigma)` ; `borne_basse=δ floor((p-w)/δ)` ; `borne_haute=δ ceil((p+w)/δ)`.

Les candidats sont triés par prix. La fusion gloutonne joint le prochain candidat à la dernière zone si la distance de leurs centres ne dépasse pas `0.03 sigma` **et** si l'enveloppe complète reste au plus `max(2δ,0.08 sigma)` de large. Le centre de l'enveloppe résultante est son milieu arrondi au tick. Ce n'est pas un centroïde pondéré. Les références sources restent dans l'enveloppe ; on ne réduit pas la largeur pour produire artificiellement un petit stop. Un candidat dont l'enveloppe après arrondi excède le plafond est omis.

Ces trois coefficients sont des **réglages d'affichage prudents et non calibrés**, pas des résultats d'étude. Si sigma=200 points (exemple fictif), la demi-largeur initiale vaut 3 points, la tolérance de fusion 6 et le plafond complet 16, avant arrondis. Ce calcul illustre les unités ; il ne décrit pas les conditions de marché actuelles.

Le nombre affiché entre crochets vaut `I(références)+I(benchmark)+I(options)`, de 1 à 3. PDH, ONH et ORH valent ensemble au plus **une** famille ; VW et PVW une ; tous les niveaux options une. Aucune indépendance statistique entre les trois familles n'est supposée. Le nombre mesure la diversité des mécanismes déclarés, pas leur qualité ni la probabilité de réaction. Des options mal documentées ne deviennent pas fiables en rejoignant une zone.

Les filtres par défaut retiennent les références à moins de 3 sigma du prix source, puis les zones avec au moins une famille, et enfin les 8 zones les plus proches. Le filtre de distance porte sur les prix candidats avant fusion. Les bornes et centres ne dépendent pas de la période du graphique. Les masques par famille déterminent seulement la présence d'une zone déjà calculée ; une zone commune à une famille cachée et une famille visible conserve toutes ses sources et son compte.

### Couche de directionnalité et événements

Le diagnostic est `ER=|C_t-O_cash| / [|C_première-minute-O_cash| + Σ|C_i-C_{i-1}|]`. Il est **cumulatif depuis le cash open**, disponible après 60 minutes, pas une fenêtre mobile de 60 bars. `ER≤0.10` : faible efficacité ; `ER≥0.25` : directionnel ; entre les deux : mixte. Pas de Hurst, demi-vie OU, test de stationnarité ni probabilité estimée. Le résultat est indisponible hors cash.

Une directionnalité élevée ou une gamma dealer saisie « Negative » atténue seulement les zones composées exclusivement de benchmark. Une option permet de les masquer ; elle est désactivée par défaut. Le modèle ne renforce pas automatiquement un niveau, ne change pas les largeurs et n'inverse pas la direction d'une transaction sur ce seul diagnostic. La saisie « Positive » est informative et n'augmente aucun score.

Les événements `YYYYMMDD-HHMM` sont horodatés dans America/New_York. Le défaut est une liste vide : aucune annonce n'est prétendument téléchargée. La fenêtre de prudence couvre 15 minutes avant et 30 après, paramétrables ; elle signale l'état dans le tableau et suspend les alertes si l'option correspondante est active. Elle ne crée aucun prix. CPI/PPI/NFP/PCE/ISM/ventes au détail/FOMC, résultats de mégacaps et rééquilibrages connus peuvent être saisis de cette manière. Le programme n'identifie ni surprise macro ni variation de liquidité.

## 3. Options : données, mécanismes et conversion

La documentation Pine consultée ne fournit pas d'API de chaîne complète d'options ou d'inventaire dealer par strike. Même un open interest par strike ne donne pas le signe des positions dealers. Chaque contrat a un long et un short. Les gammas des calls et puts longs sont tous deux positifs ; le signe d'un modèle GEX dépend de son attribution de l'inventaire, pas du nom call/put.

Pour un inventaire dealer signé q, multiplicateur M et delta Δ : `H=-ΣqMΔ`, `dH≈-ΣqM[ΓdS+Vanna dσ+Charm dt]`, avec charm défini en temps calendaire. Si le fournisseur le définit par temps restant, son signe temporel change. La GEX monétaire par mouvement de 1 % est conventionnellement `0.01 S²ΣqMΓ`. Un flip résout le zéro de ce modèle réévalué avec sa surface implicite ; il peut ne pas exister, être multiple ou varier fortement selon les hypothèses.

Gamma positive favorise des couvertures opposées au mouvement ; gamma négative des couvertures dans le même sens, toutes choses égales. Les tailles réellement couvertes, le moment de couverture, les autres produits et les flux informés peuvent dominer. Barbon–Buraschi documentent une association conditionnelle sur actions ; Cboe met en garde contre la confusion volume brut 0DTE/exposition nette. Ni–Pearson–Poteshman et Golez–Jackwerth documentent du clustering/pinning spécifique aux expirations, avec aussi **anti-pinning** sur certains contrats. Vanna, charm et 0DTE sont des canaux de flux, pas des coordonnées de prix calculables depuis les OHLCV de NQ. Ils sont exclus du calcul automatique de v1.

L'entrée accepte `CW:prix;PW:prix;ZG:prix;PIN:prix`, retours à la ligne permis, espaces autour des éléments ignorés. Au plus 12 entrées ; une entrée inconnue, mal formée ou non positive est rejetée et comptée dans le tableau. Pas de séparateur de milliers. CW/PW/ZG/PIN sont des abréviations de provenance, pas une certification de « wall » ou de gamma. Les doublons ne peuvent augmenter le nombre de familles options.

Pour des observations synchronisées clôturées t :

`r_t=Index_t/ETF_t`, `b_t=Futures_t-Index_t` ;

`prix_futures(K_ETF)=K_ETF r_t+b_t` ; `prix_futures(K_Index)=K_Index+b_t` ; `prix_futures(K_natif)=K_natif`.

Pour NQ/MNQ, les défauts sont NDX/QQQ. Pour ES/MES, utiliser Native, ou changer **les deux symboles** vers SPX/SPY. La conversion n'est pas une identité d'arbitrage ETF/options : tracking, dividendes, financement, distributions et échéance créent des écarts.

Les requêtes index/ETF sont des `request.security` de même période 1m dans le moteur 1m. Elles exigent des timestamps synchronisés, `gaps_on`, et n'utilisent pas de valeur future (`lookahead_off`). Le snapshot complet est décalé `[1]`, y compris ratio/basis/date. Le schéma `[1]+lookahead_on` des requêtes **supérieures** n'est pas nécessaire : aucune requête supérieure n'est utilisée. Recopier ce schéma sur une requête inférieure aurait d'autres effets ; la documentation les distingue.

Le défaut fige la conversion sur la première minute cash synchronisée de la session. C'est une observation vivante à cet instant, ensuite explicitement figée, afin que le niveau ne se déplace plus avec le spread. Le mode « Update each cash minute » recalcule au contraire le ratio et la base chaque minute cash clôturée ; ces zones sont alors volontairement dynamiques. Hors cash, les deux modes conservent le dernier couple synchronisé et son heure. Le code n'ajoute jamais un NQ actuel à un NDX périmé pour inventer une base en temps réel. Après 24 h de vieillissement (réglable), les conversions sont cachées. Dimanche, une conversion vendredi sera normalement périmée ; utiliser des prix natifs vérifiés ou attendre lundi.

À l'échéance, la base dépend encore des conventions de règlement et de l'ouverture des composants ; le prochain contrat garde son propre spread de financement/dividendes. Aucune constante multiplicative QQQ ni base nulle n'est codée. Aucune GEX, wall ou position dealer du jour n'a été vérifiée dans les données disponibles.

## 4. Calendrier, contrats et non-repainting

Les spécifications CME ouvertes donnent 18:00–17:00 ET, maintenance 17:00–18:00. Les défauts ne reproduisent pas un ancien arrêt 16:15–16:30 absent des spécifications actuelles. Les accumulateurs sont en America/New_York ; Europe/Paris n'est jamais converti par une constante UTC. La date de session Globex change à 18:00, y compris autour des changements de mois et DST.

Le calendrier cash Nasdaq **2026** vérifié est préchargé dans les overrides, dont les fermetures complètes et les clôtures 13:00 du 27 novembre et 24 décembre. Une alerte de tableau signale son utilisation inchangée sur une autre année. Les horaires futures de jours fériés restent distincts et configurables : consulter le calendrier CME du produit, ne pas copier les horaires cash dans les horaires futures. Des modifications d'échange et les autres années exigent une mise à jour manuelle. ES/MES utilisent le même calendrier cash américain pour cette définition de référence.

Un graphique continu demande automatiquement `syminfo.current_contract`, son **contrat daté courant**, comme historique source fixe. Un champ permet de l'imposer explicitement. Le script refuse une source continue. Ainsi, des PDH/ONH/PVW ne sont jamais hérités du précédent front-contract avec son calendar spread. La source étendue est explicitement sans backadjustment ni substitution du settlement au close. Le graphique continu peut rester backadjusté ; cela n'autorise pas à comparer nos références actuelles à de vieux prix d'un autre contrat.

`syminfo.current_contract` est un `simple string`, pas une série historique de rollovers. Il ne reconstitue pas le then-front de chaque date. Pour replay ancien, sélectionner le contrat de la période. Après roll, changer/recharger le script si nécessaire, contrôler le contrat indiqué et recréer les alertes. Les contrats datés peuvent être peu liquides avant de devenir lead-month ; le comptage de minutes complètes est une vérification de couverture, pas une garantie économique de liquidité. La remise à zéro manuelle efface les références et la fenêtre de variance ; elle exige un nouveau warmup.

Fixes après leur définition : PDH/PDL/PCC/PVW, overnight terminé, OR terminé, conversion figée, largeur une fois la nouvelle échelle de session disponible. Évolutifs par conception : VW courant, prix/distance, diagnostic de chemin, union/sélection des zones et conversion live facultative. Une zone fusionnée peut donc changer même si l'un de ses centres sources est fixe ; ce n'est pas une promesse de stabilité de chaque objet graphique. La nouvelle échelle à la clôture cash peut aussi modifier les largeurs. Les données peuvent être corrigées rétrospectivement par le fournisseur ; aucun script ne peut garantir l'absence absolue de révisions de données.

## 5. Alertes et limites de ressources

Les alertes utilisent les **bornes du snapshot précédent** pour tester la minute suivante : aucune zone VWAP recalculée avec le contact lui-même ne fabrique son propre signal. Il faut deux minutes source consécutives, un prix précédent hors de la zone, puis une intersection high–low avec les bornes fixes de cette minute. Un saut entièrement au-delà de la zone ne compte pas comme une intersection. Les alertes sont donc des notifications de contact constaté après clôture, pas des ordres limites instantanés ni des prédictions.

Le filtre par défaut exige 2 familles pour une alerte. Un cooldown global de 10 minutes, un identifiant de minute source `varip`, `alert.freq_all`, et un âge maximum de 4 minutes empêchent les répétitions à chaque tick et la reprise de toute l'histoire d'une bougie 4h. Le cooldown est global, pas par zone. Les sources plus anciennes sont ignorées ; aucune alerte historique n'est émise. Une reprise peut notifier un contact vieux de moins de 4 minutes : c'est le compromis de fraîcheur déclaré. Aucune précision de livraison à la seconde n'est promise.

Budget statique : 1 requête source, au plus 2 requêtes index/ETF imbriquées, 23 champs scalaires dans Snapshot ; aucun tuple géant. Au plus 21 candidats (9 calculés + 12 manuels), 24 boîtes, 24 lignes et 24 labels réutilisés, une table de 20 cellules, aucune création sans borne. Fenêtre de variance au plus 60 valeurs, événements 24, overrides 48 par calendrier. Jusqu'à 100 000 minutes demandées, même sur les plans dont le plafond est 100 000 ; le flux et le plan peuvent en fournir moins. Les tris portent sur les candidats, pas sur des milliers de prix, et les dessins ne sont actualisés que sur la dernière barre.

Les constantes graphiques ajoutent 8 points d’opacité de ligne et 5 de remplissage par famille supplémentaire ; l’atténuation directionnelle ajoute 25 points de transparence à la ligne et 5 au remplissage, et la bordure de tableau a 70 % de transparence. Ce sont des choix de lisibilité, sans signification statistique. La largeur de ligne ajoute un pixel par famille ; couleurs, opacités de base, taille des labels et position restent configurables.

Ces budgets sont des bornes de conception, pas une mesure de performance du moteur TradingView. Les limites de temps et mémoire doivent être testées sur 1m profond et 4h. Aucun abonnement footprint n'est exigé. Pine fournit désormais `request.footprint()` (documentation 2026), Premium/Ultimate uniquement ; son absence ancienne ne doit pas être répétée. V1 l'exclut volontairement : les catégories buy/sell sont fondées sur l'action des prix intrabar, non un carnet complet d'ordres/annulations. Les droits temps réel CME et les données NDX/QQQ restent distincts du niveau du plan TradingView.

## 6. Sélection des exclusions

| Méthode évaluée | Formule/idée | Décision et raison |
|---|---|---|
| Profil/HVN/LVN/VA | `V_j=Σq_n 1(p_n∈bin_j)`, POC=argmax V | Pas d'allocation arbitraire du volume OHLCV aux prix. Aucune preuve NQ vérifiée face à des témoins. Édition données-par-prix et validation en v2. |
| Order-flow imbalance | Somme des modifications signées des meilleures limites bid/ask, Cont et al. | Requiert prix/tailles/messages de carnet ; volume delta ne suffit pas. Aucun « absorption » inventé. |
| Nombres ronds | Clustering des ordres documenté sur FX par Osler | Grille NQ de 25/50/100 points non validée ici ; exclue. |
| VXN expected move | `IV_annuelle × sqrt(horizon)` sous convention explicite | Contexte et comparaison risque-neutre/réalisé ; pas de niveau de retournement ni allocation intraday sans saisonnalité estimée. |
| HAR-RV | Composantes quotidienne/hebdomadaire/mensuelle de RV à coefficients estimés | Pas de coefficients universels ; réalisé net de bruit et estimation hors échantillon requis. |
| Variance ratio | `VR(q)=Var(Σr)/[q Var(r)]` | VR<1 ne prouve pas stationnarité ni retour à VWAP ; corrections d'hétéroscédasticité et microstructure requises. |
| Hurst | Loi d'échelle des incréments | Plages d'échelles, stationnarité et incertitude non établies sur NQ ; pas de détecteur automatique. |
| OU/demi-vie | `t½=-Δ ln2/lnφ`, 0<φ<1 | Aucun résidu stationnaire identifié ; approximation `-ln2/b` non présentée comme exacte. |
| Saisonnalité/momentum | Variance horaire et rendements initial/final de séance | Travaux documentés mais ETF/FX ; pas de coefficients horaires NQ inventés. |
| Vanna/charm/0DTE | Sensibilités de couverture conditionnelles à l'inventaire | Données de position/surface/échéance absentes ; contexte manuel seulement. |
| Settlement | Procédure CME avec VWAP 30 secondes et règles de secours | PCC n'est pas SET ; aucune fausse reconstruction à partir d'une minute. |
| Taux, USD, liquidité, résultats, passif | Régime, événement, risque de corrélation et flux | Pas d'équation crédible donnant un niveau NQ précis à partir d'un taux réel ou d'une date ; risque/calendrier uniquement. |

## 7. Contexte actuel vérifié

Samedi **17 octobre 2026** : dernières données observées le vendredi 16 pour les indices de volatilité, jeudi 15 pour les taux cités. Les annexes donnent les endpoints officiels et leurs dates ; aucune cotation samedi n'est sous-entendue.

- VXN clôture **27,13** le 16 octobre, contre **22,89** le 15 ; augmentation calculée **18,52 %**. C'est l'implicite NDX 30 jours, pas une prévision cash NQ de demain.
- VIX 19,99 et VIX3M 20,50 au 16 : information de terme **SPX**, pas structure NDX. Taux réel Treasury 10 ans DFII10 **2,78 %** et taux effectif fed funds DFF **3,88 %** au 15 : aucun mouvement intraday ni fourchette cible Fed n'en est déduit.
- BLS CPI septembre, communiqué le 14 octobre : total +0,6 % m/m, +3,7 % a/a ; core +0,3 %, +2,6 %. BEA PCE août, publié le 30 septembre : total +0,3 % m/m, +3,4 % a/a ; core +0,2 %, +3,0 %. Pas de consensus vérifié, donc pas d'affirmation de surprise.
- La hausse récente de l'implicite justifie de réexaminer distances et risque. Elle ne justifie pas automatiquement des stops plus larges ; une zone incompatible avec le budget de perte doit être écartée. Aucun niveau de prix actuel NQ n'est calculé faute de données NQ/NDX/QQQ synchronisées réelles dans cet environnement.
- Aucun inventaire dealer, wall, flip, dates actuelles de résultats mégacaps ou biais USD/liquidité n'est vérifié. Les pages Fed de politique/calendrier et certains textes restent bloqués ; leurs données ne sont pas suppléées de mémoire.
- Prochaines annonces vérifiées : PCE 29 octobre 08:30 New York = **13:30 Paris** ; emploi 6 novembre et CPI 10 novembre 08:30 New York = **14:30 Paris**. L'écart change à cause des dates différentes de changement d'heure.

Pour VXN 27,13 %, les conversions arithmétiques sous racine du temps donnent 1,709 % par jour si convention 252 jours de trading, 1,420 % si convention 365 jours calendaires. Ce ne sont ni des taux de succès ni des intervalles prédictifs physiques calibrés. La prime de risque de variance et les annonces empêchent d'assimiler implicite et réalisé.

## 8. Validation et usage sous contraintes prop

Le banc `validation/zone_validation.py` prend vos minutes de **contrats datés** et des zones gelées avec leur date réelle de disponibilité. Il compare des témoins du même côté, mêmes largeur/échelle/durée, dans une bande locale de distances, sans consulter le futur lors du tirage. Il distingue taux de contact et taux conditionnel de réaction, classe les doubles barrières ambiguës pessimistes, applique des coûts explicites et rééchantillonne par session. Son README fixe toutes les conventions, y compris une entrée proxy à l'ouverture de la minute suivant le contact, des contrôles à prix continus et l'absence de modèle de fills/PnL.

Il ne peut pas extraire l'ancien état des objets graphiques Pine ni certifier la causalité de vos exports. **Aucun module de statistiques sur le graphique n'est inclus** : sans journal causal, utiliser la carte actuelle à rebours ferait un backtest biaisé. Les résultats sur exemples synthétiques sont uniquement des contrôles logiciels. Séparer entraînement/validation/test chronologiquement, garder un échantillon final intact et corriger l'exploration de multiples familles/paramètres. Ajouter une analyse hebdomadaire en blocs si la dépendance entre sessions l'exige.

Une largeur de zone n'est pas un stop statistiquement optimal. Pour un budget monétaire B, multiplicateur M, nombre de contrats n et coût total anticipé c en points, une distance de stop compatible doit satisfaire `n M (distance+c)≤B`. NQ M=20, MNQ M=2, ES M=50, MES M=5 dollars/point (vérifier le contrat sélectionné). Appliquer aussi le budget de perte encore disponible et les règles de drawdown trailing de la prop ; le code n'accède pas à ces comptes. N'augmenter ni taille ni confiance parce que le nombre de familles vaut 3.

## 9. V2

Priorité 1 : compilation/réception TradingView, mesure réelle des délais par période, puis journal causal exportable des zones et premier test hors échantillon sur contrats datés. Priorité 2 : calibration des largeurs/risques et saisonnalité sur données NQ propres, comparaison des familles indépendamment, statistiques de contact distinctes du PnL. Priorité 3 : édition footprint pour abonnements éligibles, sans assimiler ses classes à un OFI de carnet. Priorité 4 : service externe de chaîne d'options/surfaces/inventaires estimés, intégrant QQQ/NDX/NQ, mêmes conventions et erreurs de mesure ; l'accès arbitraire à un API externe n'est pas fourni par Pine. Priorité 5 : calendrier/settlements officiels automatisés et historique de contrats pour une vraie étude des rolls. Aucun de ces éléments n'est annoncé comme déjà implémenté.

## Annexes et références vérifiées

Les trois annexes suivantes détaillent les références complètes. Les versions à résumé seulement sont signalées ; aucune statistique quantitative n'est empruntée à un texte intégral non lu.


# Annexe A — microstructure et volatilité

# Recherche vérifiée : microstructure, repères, volatilité et diagnostics

Vérification en ligne effectuée le 17 octobre 2026. Tous les liens ci-dessous ont été ouverts dans cet environnement. Distinction essentielle : une théorie d'exécution ou une étude sur le FX/les actions ne mesure pas la probabilité de réaction de NQ à un niveau. Aucune estimation de cette probabilité n'a été produite ici. Les grades concernent la proposition précise, pas le prestige de la référence.

## Sélection recommandée

- VWAP de session calculée sur une source 1 minute fixe : mécanisme de benchmark documenté, **modéré** ; avantage de retournement intraday sur NQ : **faible/non établi**. À conserver comme référence dynamique, sans règle de retour automatique.
- Haut/bas/clôture RTH précédente, haut/bas overnight terminé, haut/bas opening range terminé : **faible**, repères descriptifs finis et observables. Aucun résultat vérifié ici ne justifie une probabilité numérique de rebond. Les conserver avec poids conservateur, regroupés dans une même famille d'extrêmes historiques pour éviter de cumuler artificiellement leurs scores.
- Échelle de volatilité basée exclusivement sur des sessions terminées : justification mathématique établie dans son modèle, robustesse NQ et multiplicateurs de zones **faibles à calibrer**. L'utiliser pour la largeur et les distances, pas comme intervalle de couverture probabiliste garanti.
- Diagnostic de persistance/efficacité : **faible** comme classifieur NQ. Si inclus, ne pas le nommer test de stationnarité, ne pas inverser automatiquement les signaux et ne pas augmenter le score d'un niveau. Affichage de prudence et réduction des zones contraires au mouvement seulement, avec règle publiée.
- Exclure du noyau : profils HVN/LVN approximatifs, absorption/exhaustion inférée d'OHLCV, vrai order-flow imbalance sans messages de carnet, grilles de nombres ronds fixes, Hurst ou demi-vie non validés, HAR-RV à coefficients arbitraires. Ces exclusions portent sur les données/validations disponibles, pas sur une preuve universelle d'inefficacité.

## 1. VWAP et contraintes d'exécution

**Mécanisme.** Les donneurs d'ordres évaluent des exécutions contre la moyenne pondérée des transactions ; les courtiers répartissent des ordres parents suivant le profil de volume pour limiter le risque de slippage à ce benchmark. Cela crée un prix économiquement interprétable. Les modèles ouverts ne disent pas que les courtiers doivent défendre le VWAP courant, ni que le prix doit revenir vers lui. Un algorithme VWAP programme ses quantités dans le temps ; ce n'est pas nécessairement un ordre limite permanent au prix VWAP.

**Formule exacte aux transactions** : `VWAP_t = sum_{j<=t}(p_j q_j)/sum_{j<=t}q_j`. En temps continu : `integral_0^t S_u V_u du / integral_0^t V_u du`.

**Implémentation OHLCV** : `x_i=(H_i+L_i+C_i)/3`, `vwap_t=sum(v_i*x_i)/sum(v_i)` sur minutes closes et sur une session déterminée. Il s'agit d'une **approximation de VWAP de transactions**, même sur 1 minute. Un volume nul ne doit pas provoquer de division ; sans volume, le VWAP est indisponible et ne doit pas devenir une moyenne temporelle silencieusement.

Les écarts pondérés `s²=sum(v_i*x_i²)/sum(v_i)-VWAP²` décrivent la dispersion des prix échangés approximés. Ils ne constituent ni une variance de rendements futurs ni une estimation sans biais sous poids arbitraires. `VWAP±k*s` n'a donc pas une couverture gaussienne documentée. Une tendance peut déplacer VWAP et maintenir le prix loin de celui-ci pendant toute la séance.

**Sources ouvertes et vérifiées :**

1. Olivier Guéant et Guillaume Royer (2014, version de travail révisée), *VWAP execution and guaranteed VWAP*. arXiv:1306.2832v4. [Notice](https://arxiv.org/abs/1306.2832), [texte intégral](https://arxiv.org/pdf/1306.2832). La notice vérifie auteurs/titre et le PDF a été lu. Extrait, p.2 : « Many agents are willing to trade as close as possible to the VWAP as they are benchmarked on the VWAP. » Étude théorique de liquidation/impact et du contrat garanti ; pas étude de rebonds NQ.
2. Takashi Kato (2015), *VWAP execution as an optimal strategy*, **JSIAM Letters**, 7, 33–36, DOI [10.14495/jsiaml.7.33](https://doi.org/10.14495/jsiaml.7.33). Version longue ouverte : [arXiv:1408.6118v4](https://arxiv.org/abs/1408.6118), [PDF](https://arxiv.org/pdf/1408.6118). Extrait du résumé : « VWAP strategy is the optimal execution strategy for a risk-neutral trader ». Ce résultat est conditionnel au modèle Almgren–Chriss généralisé, à l'impact temporaire dépendant du volume et à la neutralité au risque ; il ne prouve pas la supériorité universelle ni un effet de support/résistance. Utiliser le DOI de la notice arXiv ; la note de bas de page du PDF contient un DOI manifestement différent, qui n'est pas repris ici.
3. Enzo Busseti et Stephen Boyd (2015), *Volume Weighted Average Price Optimal Execution*, [arXiv:1509.08503](https://arxiv.org/abs/1509.08503). Notice et résumé ouverts ; modèle de minimisation moyenne–variance du slippage avec coûts quadratiques et simulations sur données NYSE. Ce n'est pas une mesure NQ ; aucun résultat chiffré n'est transféré au présent indicateur.

**Grade** : modéré pour la pertinence pratique du benchmark (plusieurs travaux cohérents dont un article), faible pour une probabilité de retournement à ce prix sur NQ.

## 2. OFI, delta et ce qu'une bougie ne révèle pas

Rama Cont, Arseniy Kukanov et Sasha Stoikov (2014), *The Price Impact of Order Book Events*, **Journal of Financial Econometrics**, 12(1), 47–88. DOI [10.1093/jjfinec/nbt003](https://doi.org/10.1093/jjfinec/nbt003). [Notice universitaire arXiv](https://arxiv.org/abs/1011.6402), [texte intégral de travail, 2011](https://arxiv.org/pdf/1011.6402). La notice confirme la publication. PDF lu, notamment résumé et définition OFI.

Leur observation porte sur des actions américaines ; le carnet comporte les prix et tailles au meilleur bid/ask, et leurs variations. Extrait du résumé : « price changes are mainly driven by the order flow imbalance, defined as the imbalance between supply and demand at the best bid and ask prices ». La relation volume échangé/prix est plus bruitée et moins robuste dans leur étude.

Pour un événement n, notant `P^B,q^B,P^A,q^A` les meilleures limites et tailles :

`e_n = 1(P^B_n >= P^B_{n-1})q^B_n - 1(P^B_n <= P^B_{n-1})q^B_{n-1} - 1(P^A_n <= P^A_{n-1})q^A_n + 1(P^A_n >= P^A_{n-1})q^A_{n-1}` ;

`OFI_k=sum_{n in interval k}e_n`, puis `Delta midprice_k ≈ beta_k OFI_k`, où beta dépend inversement de la profondeur dans le modèle empirique.

Un retrait de limite au bid et un ordre de vente agressif ont un effet similaire sur la file ; les deux sont pris en compte, alors qu'un delta de transactions n'observe pas les annulations. Une répartition du volume de sous-bougies selon leur direction n'identifie pas ces événements. Un footprint de volume ou un delta de transactions, s'il est disponible dans le plan, ne reconstitue pas non plus automatiquement le flux de limites et d'annulations. **Aucun vrai OFI ni absorption identifiée n'est calculé dans le noyau.**

**Grade** : modéré pour l'étude empirique précise, non transférable sans nouvelles données à un modèle de niveaux NQ. Le mécanisme offre surtout une raison de ne pas surinterpréter OHLCV. Échec : profondeur variable, latence, plateformes/actifs différents, évènements non observés.

## 3. Nombres ronds et support/résistance : preuve circonscrite au FX

1. Carol Osler (2000), *Support for Resistance: Technical Analysis and Intraday Exchange Rates*, **Federal Reserve Bank of New York Economic Policy Review**, 6(2), 53–68. [Page primaire](https://www.newyorkfed.org/research/epr/00v06n2/0007osle.html), [PDF lu](https://www.newyorkfed.org/medialibrary/media/research/epr/00v06n2/0007osle.pdf).
2. Carol L. Osler (2003), *Currency Orders and Exchange Rate Dynamics: An Explanation for the Predictive Success of Technical Analysis*, **Journal of Finance**, 58(5), 1791–1819. Référence de publication confirmée par la [notice primaire NYFed Staff Report 125](https://www.newyorkfed.org/research/staff_reports/sr125.html). [Version de travail ouverte et lue](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr125.pdf), mars/avril 2001.

Dans le premier travail, les niveaux diffusés par six sociétés actives sur le FX sont comparés à des cours intraday de devises (1996–1998). La page précise que la force prédictive varie selon les devises et les sociétés. Dans le second, les stop-loss et take-profit d'une banque FX se regroupent à des nombres ronds ; leurs distributions diffèrent, de sorte qu'un même voisinage peut arrêter ou accélérer une tendance suivant les types d'ordres. Extrait confirmé du résumé : « The requested execution rates of these orders are strongly clustered at round numbers ».

**Limite de transfert.** Ces deux travaux sont liés, ne constituent pas des réplications indépendantes sur futures Nasdaq, et n'autorisent pas une grille NQ de 25/50/100 points choisie arbitrairement. Un grand nombre de réactions visuelles à des grilles denses est inévitable par construction. Le mécanisme n'identifie pas en direct le stock d'ordres actuel.

**Grade** : modéré pour les observations FX ; faible pour les nombres ronds NQ et pour l'hypothèse que PDH/PDL/ONH/ONL/OR ont un avantage quantifié. Recommandation : pas de famille ronds activée par défaut. Les extrêmes historiques ont une définition stable et un intérêt descriptif, mais doivent être présentés comme hypothèses à tester, pas comme niveaux validés par Osler.

## 4. Volume-at-price, HVN, LVN, POC et value area

Le profil exact de transactions, pour un bin de prix `B_j`, est `V_j=sum_n q_n 1(p_n in B_j)`. `POC=argmax_j V_j`; HVN/LVN exigent une règle explicite de lissage/voisinage. Une value area contenant alpha du volume dépend aussi d'un algorithme de construction (la réunion des bins les plus volumineux peut être disjointe ; une expansion contiguë depuis le POC produit un autre résultat). Le seuil usuel 70 % n'est pas dérivé d'une couverture normale de rendements.

Un volume passé élevé peut signaler beaucoup d'échanges et d'inventaires ; il ne mesure pas les limites encore présentes ni le prix auquel ces inventaires ont été revendus. Un faible volume historique n'identifie pas une faible liquidité future. La conservation des volumes par prix sur une bougie OHLCV est impossible sans données intrabar/trades : allouer uniformément son volume sur high–low ou tout attribuer à HLC3 constitue un modèle d'allocation, pas une observation.

**État de la preuve dans les sources ouvertes ici** : aucune étude vérifiée établissant que les HVN/LVN d'un profil approximé prédisent des réactions NQ après coûts, face à des niveaux placebo appariés. Cela n'est pas une conclusion de non-existence dans toute la littérature. **Grade faible** pour l'usage proposé. Exclusion du noyau v1 ; roadmap avec volume réellement par prix, stabilité aux bins, définition préalable et validation indépendante.

## 5. Volatilité de plage : formules vérifiées et portée

Pour une session terminée d, définir `h=log(H_d/O_d)`, `l=log(L_d/O_d)`, `c=log(C_d/O_d)`.

- Parkinson : `vP_d=(h-l)^2/(4 log 2)=log(H_d/L_d)^2/(4 log 2)`.
- Rogers–Satchell : `vRS_d=h(h-c)+l(l-c) = log(H/O)log(H/C)+log(L/O)log(L/C)`.
- Estimation glissante de variance de session : `vbar_d=(1/n)sum_{j=1}^n v_{d-j}` et `sigmaLog=sqrt(vbar_d)` ; inclure uniquement les sessions terminées. Une moyenne exponentielle est un choix de lissage distinct, à documenter ; une moyenne de racines n'est pas la racine d'une moyenne de variances.
- Conversion locale en points à un ancrage connu `A` : `sigmaPoints≈A*sigmaLog`. Sous modèle lognormal, bornes de rendement à un horizon donné : `A exp(±k*sigmaLog)` ; elles ne sont pas l'amplitude high–low attendue, ni des barrières de rebond.

Parkinson suppose en particulier une diffusion continue à drift nul ; Rogers–Satchell est insensible au drift constant dans ce modèle. Ni l'un ni l'autre ne mesure le gap séparant la clôture précédente de l'open courant. Une session cash laisse donc l'information overnight hors de sa variance interne ; ce point doit être visible. Jumps, haltes, extrêmes échantillonnés et nouvelles programmées fragilisent les interprétations probabilistes. Les performances théoriques des estimateurs ne valident pas le coefficient de largeur d'une zone.

**Sources vérifiées :**

1. Michael Parkinson (1980), *The Extreme Value Method for Estimating the Variance of the Rate of Return*, **The Journal of Business**, 53(1), 61–65. DOI [10.1086/296071](https://doi.org/10.1086/296071). Identité bibliographique ouverte via [métadonnées déposées chez Crossref](https://api.crossref.org/works/10.1086/296071). Le texte original n'était pas lisible via Chicago/JSTOR ; ne pas prétendre l'avoir lu intégralement.
2. L. C. G. Rogers et S. E. Satchell (1991), *Estimating Variance From High, Low and Closing Prices*, **The Annals of Applied Probability**, 1(4), 504–512. DOI [10.1214/aoap/1177005835](https://doi.org/10.1214/aoap/1177005835). Identité et résumé auteur ouverts via [Crossref](https://api.crossref.org/works/10.1214/aoap/1177005835). Le résumé dit « unbiased whatever the drift c » et avertit des erreurs parfois importantes liées aux extrêmes discrètement échantillonnés. Le serveur Euclid a renvoyé une page challenge et non le texte complet.
3. Alexander Saichev et Svetlana Lapinova (2012), *Comparative statistics of Garman-Klass, Parkinson, Roger-Satchell and bridge estimators*, [arXiv:1202.4311](https://arxiv.org/abs/1202.4311), [PDF ouvert et lu](https://arxiv.org/pdf/1202.4311). Formules exactes p.2, équations (3), (5), avec high/low/close des incréments de log-prix. Cadre Brownien explicite p.2, équation (9). C'est cette source ouverte qui vérifie directement les formules ici ; les références d'origine ci-dessus vérifient leurs auteurs et la provenance.

**Grade** : modéré pour les méthodes vérifiées et leur justification dans le cadre Brownien ; avantage pratique NQ et choix de largeur faible/non calibré. Le grade fort au sens de réplications empiriques indépendantes ne doit pas être attribué à la réaction sur ces bandes. Ne pas qualifier le modèle de bandes de probabilité empiriquement validées.

## 6. HAR-RV et saisonnalité : prévoir le risque n'est pas situer un retournement

Fulvio Corsi (2009), *A Simple Approximate Long-Memory Model of Realized Volatility*, **Journal of Financial Econometrics**, 7(2), 174–196, DOI [10.1093/jjfinec/nbp001](https://doi.org/10.1093/jjfinec/nbp001). [Métadonnées de l'éditeur via Crossref](https://api.crossref.org/works/10.1093/jjfinec/nbp001), [notice avec résumé éditeur](https://ideas.repec.org/a/oup/jfinec/v7y2009i2p174-196.html). Publication 2009 ; mise en ligne anticipée le 7 novembre 2008, ce n'est pas une incohérence. Résumé vérifié, texte intégral original non accessible. Le résumé confirme un modèle autorégressif de composantes de volatilité à plusieurs horizons et précise l'absence de vraie propriété de mémoire longue du modèle.

Représentation canonique à estimer (ne pas présenter comme implémentée dans v1) : `RV_{d+1}=beta0+betaD RV_d+betaW mean(RV_d..RV_{d-4})+betaM mean(RV_d..RV_{d-21})+epsilon`. Variantes en log-RV demandent correction de retransformation et protocole distinct. Le modèle exige de la realized variance sur données intraday nettoyées, une estimation passée des coefficients et un test hors échantillon. Copier des coefficients universels ou baptiser une simple moyenne « HAR » serait incorrect. **Exclu de v1**, roadmap.

Torben G. Andersen et Tim Bollerslev (1997), *Heterogeneous Information Arrivals and Return Volatility Dynamics: Uncovering the Long-Run in High Frequency Returns*, **Journal of Finance**, 52(3), 975–1005. Version de travail (1996), NBER 5752, DOI [10.3386/w5752](https://doi.org/10.3386/w5752). [Notice primaire](https://www.nber.org/papers/w5752), [PDF lu](https://www.nber.org/system/files/working_papers/w5752/w5752.pdf). Notice confirme la publication. Pages 3–5 du WP : périodicité intraday prononcée et difficulté de distinguer dépendance de volatilité et cycle horaire ; pages 5–6 : effets différents selon les annonces. Données principales DM/USD, pas NQ. **Modéré** pour ce résultat empirique précis ; principe de saisonnalité largement documenté mais pas une calibration NQ fournie ici.

Conséquence pratique : pour un horizon h après le cash open, remplacer `sqrt(h/T)` par une fraction de variance saisonnière `sqrt(F(h))` seulement si `F` est estimée sur les mêmes données NQ et hors échantillon. Sans calibration, le temps carré-racine doit être étiqueté approximation de diffusion homogène, particulièrement inadéquate près du cash open ou d'un CPI/FOMC. Les horaires ne créent pas de niveau de prix en eux-mêmes.

Lei Gao, Yufeng Han, Sophia Zhengzi Li et Guofu Zhou (2018), *Market intraday momentum*, **Journal of Financial Economics**, 129(2), 394–414, DOI [10.1016/j.jfineco.2018.05.009](https://doi.org/10.1016/j.jfineco.2018.05.009). [Notice et résumé de l'éditeur reproduits par RePEc](https://ideas.repec.org/a/eee/jfinec/v129y2018i2p394-414.html), [métadonnées DOI](https://api.crossref.org/works/10.1016/j.jfineco.2018.05.009). Auteurs et titre confirmés, résumé lu ; texte complet pas revendiqué. Étude des ETF, principalement S&P500 1993–2013 : le rendement première demi-heure depuis la clôture précédente prédit celui de la dernière demi-heure, relation plus forte les jours volatils/à annonces. **Modéré** pour cette étude ; cela ne démontre ni une règle de continuation NQ à toute heure ni un retournement sur ORH/ORL. Exclusion de tout biais directionnel automatique fondé sur ce seul résultat.

## 7. Variance ratio, Hurst et demi-vie : diagnostics insuffisants seuls

Andrew W. Lo et A. Craig MacKinlay (1988), *Stock Market Prices Do Not Follow Random Walks: Evidence from a Simple Specification Test*, **The Review of Financial Studies**, 1(1), 41–66. Version NBER 2168 (1987), DOI [10.3386/w2168](https://doi.org/10.3386/w2168). [Notice primaire lue](https://www.nber.org/papers/w2168), [PDF ouvert](https://www.nber.org/system/files/working_papers/w2168/w2168.pdf). Le résumé souligne explicitement : « the rejection of the random walk cannot be interpreted as supporting a mean-reverting stationary model of asset prices ».

`VR(q)=Var(sum_{j=0}^{q-1}r_{t-j}) / (q Var(r_t))`. Avec covariance-stationnarité et variance finie : `VR(q)=1+2 sum_{k=1}^{q-1}(1-k/q)rho(k)`. Sous incréments non corrélés, la valeur théorique est 1. Sur échantillon fini, il faut les corrections d'estimation et une inférence robuste à l'hétéroscédasticité ; un simple seuil 0,8/1,2 n'est pas le test original. `VR<1` décrit des autocorrélations négatives agrégées à ces lags, pas une stationnarité du niveau ni un retour vers une référence choisie. Les sauts, la saisonnalité et le bid–ask bounce altèrent la lecture.

Andrew W. Lo (1991), *Long-Term Memory in Stock Market Prices*, **Econometrica**, 59(5). Version primaire vérifiée : NBER Working Paper 2984 (1989), DOI [10.3386/w2984](https://doi.org/10.3386/w2984), [notice](https://www.nber.org/papers/w2984). La notice confirme revue/date. Résumé : « no evidence of long-range dependence ... once short-term autocorrelations are taken into account ». Ne pas répéter comme résultat universel NQ ; c'est une critique justifiée de l'interprétation naïve du R/S.

Un estimateur Hurst `Var(x_{t+h}-x_t) proportional h^(2H)` repose sur stationnarité des incréments et une vraie plage d'échelles ; un slope de régression sur quelques horizons n'identifie pas un régime profitable. H<0,5 n'est pas une garantie de retour à VWAP, H>0,5 pas un signal de breakout.

Pour l'OU `dX=kappa(mu-X)dt+sigma dW`, la moyenne conditionnelle vérifie `E[X_{t+h}-mu|X_t]=exp(-kappa h)(X_t-mu)` ; la demi-vie est donc `ln(2)/kappa`. Échantillonné tous les Delta : `X_{t+Delta}-mu=phi(X_t-mu)+epsilon`, `phi=exp(-kappa Delta)`, demi-vie `-Delta ln(2)/ln(phi)` si `0<phi<1`. Régression en différences `Delta X=a+b X_{t-1}+epsilon` : `phi=1+b`; `-ln(2)/b` n'est qu'une approximation quand b est petit. Ce passage est une dérivation mathématique, pas un résultat empirique cité. Avec phi≥1 pas de demi-vie de retour finie ; avec phi≤0 pas une discrétisation OU à kappa réel positif. Estimer cela sur NQ brut, un spread non stationnaire ou des résidus d'un VWAP qui évolue invalide l'interprétation OU.

**Décision** : diagnostics VR/Hurst/demi-vie exclus du filtrage de niveaux v1 faute de modèle stationnaire validé, de correction saisonnière et d'inférence robuste. Un efficiency ratio purement descriptif peut être moins ambitieux, mais reste un choix heuristique. Aucun seuil n'est une probabilité estimée de maintien d'un niveau.

## 8. Confluence et zones : règles d'honnêteté proposées

Une unité de volatilité doit rester la même pour tous les centres comparés pendant un instant donné. Une demi-largeur `w=max(tick, round_to_tick(k*sigmaPoints))` est une **heuristique d'affichage** ; elle ne devient pas un stop recommandé. Une zone trop large par rapport au budget de risque doit être ignorée ou détectée comme inutilisable, jamais comprimée artificiellement pour donner une fausse précision.

Fusionner des centres ne prouve pas indépendance : haut veille, haut nuit et haut OR peuvent être le même extrême poursuivi par les mêmes acteurs. Pour les scores, utiliser le **maximum par famille de mécanisme**, puis la somme entre familles ; ne pas compter trois sous-références comme trois confirmations. Le score n'est pas une probabilité et n'est pas une quantité issue des références. Ne pas l'appeler « force statistique ». Une moyenne pondérée du centre peut créer un niveau que personne ne surveille : afficher les sources et étendre les bornes pour contenir les centres originaux, avec un plafond de largeur documenté, ou s'abstenir de fusionner une chaîne trop large.

## 9. Validation nécessaire, aucune statistique de performance inventée

Gel préalable de chaque centre, largeur, disponibilité et de l'information de régime. Définir le premier contact seulement après publication du niveau, avec cooldown et un seul événement indépendant par zone/session. Comparer des niveaux témoins de mêmes distances au prix, largeur, moment de disponibilité, côté, durée de vie, volatilité et jours d'annonce. Une grille aléatoire uniforme sur tout l'écran est une mauvaise baseline.

Définir avant mesure une réaction (p.ex. excursion opposée de a sigma avant traversée de b sigma, dans h minutes). Les seuils a,b,h sont paramètres de recherche, pas valeurs validées. Si une même bougie touche à la fois le seuil de succès et d'échec, l'ordre est inconnu à cette résolution : utiliser données plus fines ou classer ambigu, sans choisir favorablement. Les intervalles de confiance et bootstrap doivent regrouper par session (pas traiter contacts successifs comme indépendants). Validation chronologique, périodes de roll/jours fériés identifiées, vrai contrat et coûts bid–ask/commissions/slippage. Contrôler multiplicité des familles/paramètres, publier n, taux témoins, différence, incertitude et résultats non concluants. Une réaction n'est pas un PnL de stratégie et une taille d'échantillon importante n'annule pas le biais de sélection.

## Vérification numérique des identités

Contrôle Python standard-library, graine 20261017 : 10 000 quadruplets OHLC synthétiques cohérents ; équivalence des deux écritures Rogers–Satchell, non-négativité, équivalence des écritures Parkinson (tolérance 1e-14). Cinq coefficients OU phi entre 0,01 et 0,99 vérifient phi^demi_vie=0,5. Tous les contrôles passent. Ce sont des vérifications algébriques, pas un backtest ni des observations de marché.


# Annexe B — options, conventions et contexte

# Options, contract conventions and macro: verified research inputs

Verified online in this execution on 2026-10-17 (Europe/Paris client date; Saturday). This note distinguishes published mechanisms, demonstrated sample-specific effects, and untested NQ trading rules. Official source content was opened and read, not inferred from URL titles. Primary-source numbers below are exactly the releases returned by those official endpoints. All source data refer to their indicated observation dates, not Saturday trading.

## Evidence scale

An exchange specification is authoritative for a contract convention, but is not evidence of a profitable reaction rule. A mathematical identity is strong as an identity, but does not identify dealer inventories. Single peer-reviewed empirical studies are moderate evidence under the user's definition. Related results on stocks and S&P futures support expiration pinning as a real phenomenon across samples; they do not establish NQ 1-minute reversal probabilities. No NQ tick-level effect or reaction rate has been estimated here.

## Dealer gamma, flips and walls

Let signed dealer option inventory be q_i (positive long), multiplier M_i, underlying S, option delta Δ_i and gamma Γ_i. The inventory hedge in underlying units is H = -Σ q_i M_i Δ_i. To first order, holding positions and volatility fixed:

    dH = -Σ q_i M_i Γ_i dS.
    dollar GEX per 1% move = 0.01 S² Σ q_i M_i Γ_i.

For futures hedges, divide underlying-equivalent exposure by the futures multiplier, with the appropriate cross-product sensitivity. A positive gamma dealer hedges by selling an increase and buying a decrease; negative gamma reverses the flow. This is a conditional flow mechanism, not an unconditional prediction: hedging time, netting across products, competing informed flow, liquidity and discrete execution matter.

Open interest OI_i is not signed dealer q_i. Every open contract has a long and a short. Assigning dealers long calls/short puts or the reverse from OI alone is an assumption, not observed positioning. Black-Scholes long call and long put gammas are both positive:

    Γ = exp(-q τ) φ(d1) / (S σ sqrt(τ)).

A gamma flip solves G(S*) = Σ q_i M_i Γ_i(S*, σ_i(S*), τ_i) = 0 under an explicitly specified inventory and volatility-surface model. There can be no root, more than one root, or an unstable root. Moving the spot through a provider's quoted flip does not mechanically cause all dealers to change sign. A call/put wall is not standardized: it might maximize call/put OI, gamma-weighted OI, modeled signed gamma or another measure. Store the definition, provider, underlying, timestamp and expiry universe with every manually supplied level.

**Evidence:** moderate for a gamma–intraday momentum/reversal association in a broad stock-options panel (Barbon and Buraschi working-paper abstract verified); weak for a fixed NQ flip/wall being a reversal zone. Cboe's primary SPX evidence explicitly contradicts equating huge 0DTE gross volume with huge net hedging. Thus include manual contextual levels only with separate attribution; do not derive or fabricate GEX from futures OHLCV. No causal grade upgrades from multi-family confluence.

## Vanna, charm, 0DTE and expiration pinning

With calendar-time charm C_i = ∂Δ_i/∂t and vanna V_i = ∂Δ_i/∂σ:

    dH ≈ -Σ q_i M_i [Γ_i dS + V_i dσ + C_i dt].

If charm is instead defined as ∂Δ/∂τ for remaining time τ, its calendar-time term has the opposite sign. Positions, implied-volatility changes and the hedge convention are all required. Vanna/charm are exposures/flow channels, not unique price coordinates. Exclude computed vanna/charm levels from OHLCV-only v1; externally researched levels can be pasted as explicitly manual context. As τ→0, near-ATM gamma may become large, but far-from-ATM gamma collapses, and same-day trading changes inventory. A morning OI snapshot is particularly weak for 0DTE intraday net positioning.

**Verified expiration evidence:** Ni, Pearson and Poteshman find expiration-date stock-price clustering at strikes and evidence consistent with market-maker hedge rebalancing and proprietary trading. Golez and Jackwerth find S&P500 futures pulled toward the ATM futures-option strike on serial-option expiry, but **pushed away** from the carry-adjusted ATM index-option strike before index-option expiry (anti-cross-pinning). Avellaneda and Lipkin provide a price-impact/delta-hedging model with a finite pinning probability. These are specific expiry/instrument/settlement mechanisms. A generic 'largest OI strike attracts price every day' rule is unsupported. Options on NDX, QQQ and NQ have different settlement and exercise conventions; do not treat their expirations as interchangeable or apply stock-pin empirical magnitudes to NQ.

**Verified Cboe counterevidence:** Mandy Xu's 2023 exchange study sees customer/market-maker, buy/sell, open/close flags for SPX transactions, unlike OI-based outside estimates. It reports balanced net flow and no discernible rise in SPX intraday/gap volatility in its studied period. The study expressly notes potential offsets in other expiries/products and hedging with other options. Its conclusion is historical SPX evidence, not a claim that 0DTE can never matter, and not evidence about today's NQ inventory.

**Grades:** moderate for the individual pinning/anti-pinning empirical studies; mathematical mechanism/model only for Avellaneda–Lipkin; moderate exchange evidence for the Cboe sample; weak for an unconditional NQ wall/flip/pinning trading rule. No current dealer sign, gamma-flip, wall, vanna or charm figure has been verified. Current positioning is **unknown**.

## Mapping QQQ / NDX option levels into NQ

At a synchronized observation t with cash prices observed, define:

    r_t = NDX_t / QQQ_t,
    b_t = NQ_t - NDX_t,
    mapped(QQQ strike K) = K r_t + b_t,
    mapped(NDX strike K) = K + b_t,
    mapped(NQ strike K) = K.

Round final chart prices to syminfo.mintick. This is a local mapping of equivalent index exposures, not an options-arbitrage identity across ETF and index. QQQ fees, tracking, cash distributions, cash-market price differences and basis all affect r_t; the same r_t is only a local scale approximation for nearby strikes. CME fair-value documentation confirms basis reflects financing, dividends and time to expiry; actual futures also differ from theoretical fair value because of supply/demand. Its published illustrative formula is F = Cash[1+r(days/360)] − dividends; its settlement fallback uses a different day-count convention. Do not hardcode a QQQ multiplier or assume zero basis.

Use request.security for each explicitly selected source and a synchronized confirmed timestamp. A requirement to convert using the *live* ratio/basis means mapped levels move as those inputs move. It conflicts with treating mapped manual zones as immutable session references. Resolve explicitly: freeze the conversion at a confirmed cash-session observation and label its timestamp, while permitting a clearly labeled live mode if implemented. At 09:30 before a minute closes no synchronized confirmed current-day conversion exists. Outside the cash session, a held-last NDX value combined with live NQ makes b_t absorb essentially the entire NQ price move, spuriously dragging every manual zone alongside the market; do not call that a live verified basis. Freeze the last synchronized conversion and show staleness, or suppress converted levels until cash data return. A newly entered Sunday level therefore uses stale Friday conversion until Monday cash opens unless the user supplies actual NQ coordinates. Do not silently use stale cash prints as fresh observations.

Near expiry fair-value basis tends toward its final-settlement linkage, but SOQ constituents do not necessarily open simultaneously and NDX AM/PM options settle differently. The next quarterly futures contract can have a nonzero financing/dividend calendar spread; continuous-futures rolls change the coordinate system. An explicit current contract is safest. Do not shift inherited levels by an inferred gap or claim a heuristic gap detector identifies all rolls. Back-adjusted continuous history can itself be rewritten after a roll. A manual roll/reset date and resetting accumulated session state avoids carrying old-contract levels, but cannot reverse every vendor historical adjustment; disclose this limitation.

For ES/MES the relevant index/ETF defaults are SPX/SPY, not NDX/QQQ. All such source symbols must be configurable or detected per root; an NQ-specific source must never quietly map to ES.

## Verified contract, session, roll and settlement conventions

The current CME product page is JavaScript rendered. Its own client script exposes the actual official specification API, which was opened successfully:

- NQ: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/146
- MNQ: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/8668
- ES: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/133

| Contract | Multiplier | Outright tick | Dollar tick |
|---|---:|---:|---:|
| NQ | $20/index point | 0.25 | $5.00 |
| MNQ | $2/index point | 0.25 | $0.50 |
| ES | $50/index point | 0.25 | $12.50 |

All three specifications say Globex Sunday 18:00 through Friday 17:00 Eastern, with daily maintenance 17:00–18:00 Eastern. The current specifications do **not** give the historical additional 16:15–16:30 halt. CME ClearPort reporting hours differ and must not be mistaken for Globex trading hours. Nasdaq official equity cash hours are weekdays 09:30–16:00 ET. Encode these with America/New_York IANA timezone and explicit session inputs, never fixed Paris UTC offsets. Cash weekdays differ from Globex trade dates that begin the preceding evening.

NQ final expiry is ordinarily 09:30 ET on the third Friday of the quarterly month. Rule35903 states final settlement is the special opening quotation based on Nasdaq Official Opening Prices of index components; holiday and missing-stock rules apply. Current official CME roll guidance says the customary lead-month roll is the **Monday before** the third Friday (not the older Thursday convention). It explicitly allows participants to roll at any time; TradingView's continuous roll choice need not be the same. The verified table lists Dec2026 roll December14, expiration December18. June2026 expiry is June18 because of the holiday exception; don't derive every expiry with an unconditional third-Friday function.

**Daily settlement is not a session close.** CME's settlement page says lead-month NQ daily settlement Tier1 is trade VWAP in **14:59:30–15:00:00 CT = 15:59:30–16:00:00 ET**. Tier2 is bid/ask midpoint when no trade; Tier3 uses an index/carry fallback. Other months use calendar-spread rules. A 1-minute cash close, a 17:00 ET Globex close, or request.security daily close is not independently verified as this settlement. With only minute OHLCV a script cannot reconstruct the 30-second trade VWAP or fallback order book. Use manually verified official settlement if desired, or label prior cash/futures close accurately and omit settlement. Never call an approximation 'SET'.

Holidays require exchange calendars, not just absence of 09:30 bars (futures can trade on a cash holiday). Official Nasdaq2026 table has full closures Jan1, Jan19, Feb16, Apr3, May25, Jun19, Jul3, Sep7, Nov26, Dec25; cash early closes Nov27 and Dec24 at13:00ET. CME holiday hours are separate, product-specific and subject to change. A reusable script needs configurable early-close/skip-date overrides and must disclose any finite calendar coverage. No trading bars during maintenance should enter overnight or cash accumulations.

## Current verified context, as of 17 October 2026, Europe/Paris

It is Saturday. Latest exchange volatility observations returned are Friday16October, and the latest rates observations below are Thursday15October. These dates must appear with the numbers.

| Measure | Verified latest observation | Source and interpretation |
|---|---|---|
| VXN | 2026-10-16: O22.54, H28.17, L22.41, **C27.13** | Official Cboe historical CSV; prior10/15 close22.89, one-day change18.5234%, calculated from those two observed closes. NDX 30-day option-implied volatility, not today's NQ reaction rate. |
| VIX | 2026-10-16 C19.99 | Cboe official CSV; S&P500 implied volatility, different underlying. |
| VIX3M | 2026-10-16 C20.50 | Cboe official CSV; VIX/VIX3M=0.97512, calculated. This pair is consistent with slightly higher 3-month than 30-day S&P implied vol; it does not establish NDX term structure. |
| 10-year real Treasury yield DFII10 | **2.78% on2026-10-15** | FRED official series page, updated10/16 15:16CDT. Level only; a direction or intraday change was not verified. |
| Effective fed funds DFF | **3.88% on2026-10-15** | FRED official page, updated10/16. It is an effective overnight rate, not a verified current target range. |
| September CPI | Release2026-10-14: headline +0.6%m/m,+3.7%y/y; core +0.3%m/m,+2.6%y/y | BLS actual release. Inflation surprise versus consensus was not verified, so do not call this a surprise. |
| August PCE prices | Release2026-09-30: headline +0.3%m/m,+3.4%y/y; core +0.2%m/m,+3.0%y/y | BEA actual release. These are August data, not September CPI-comparable same-month data. |
| September payrolls | Release2026-10-02: +29,000; unemployment4.2%; AHE +0.1%m/m,+3.0%y/y | BLS actual release; says payrolls/unemployment changed little. No consensus or market reaction verified. |

VXN's27.13 annualized reading yields a **heuristic trading-day** standard-deviation scale27.13/sqrt252=1.70903% and a **calendar-day** scale27.13/sqrt365=1.42005%. These are computed mathematical conversions under explicitly chosen square-root-time assumptions, not measured next-day prediction intervals, not an expected high-low range and not automatically68% physical coverage. Cboe's official VXN methodology targets30-day implied NDX volatility using NDX/NDXP options; the annual calendar convention and risk-neutral/physical distinction must be respected. A static30-day reading cannot allocate a specific fraction to cash hours, overnight or an announcement minute without additional assumptions. If code uses252 it must label this a trading-day scaling convention and validate empirical coverage separately.

**Practical interpretation supported by these observations:** the VXN increase justifies checking updated volatility-scaled distances and avoiding stale fixed-point widths. It does not tell us to widen every stop or trade larger zones: a zone beyond the prop-risk budget should be excluded. Rates and inflation are macro state information, not NQ support prices. Without announcement surprises, actual dealer inventory, current strike distributions, synchronized NQ/NDX/QQQ prices, positioning or earnings filings, there is no verified current directional bias, wall, flip or numerical NQ support/resistance level. Do not invent any.

Next releases explicitly announced in the opened official releases:

- BEA September personal income/outlays:2026-10-29 at08:30EDT =13:30 Europe/Paris, because Europe has switched to winter time and the US has not yet.
- BLS October employment situation:2026-11-06 at08:30ET =14:30 Europe/Paris.
- BLS October CPI:2026-11-10 at08:30ET =14:30 Europe/Paris.

The Fed calendar, latest policy statement and open-market pages still returned HTTP403. Do not claim a current FOMC target band or next meeting date from memory. Nasdaq methodology PDF also returned403, so no verified current rebalance or component-weight claim is used. Current mega-cap earnings dates, dollar/liquidity trend, intraday rates moves, NDX IV term structure, and dealer positioning remain unverified. Their role is scheduled risk/volatility or bias, generally not a precise horizontal level. Manual event dates should change a risk indicator, alert policy or level eligibility; they should not manufacture prices. This partial source failure does not block using verified primary and academic sources elsewhere.

## Full verified bibliography and verification scope

1. Sophie Xiaoyan Ni, Neil D. Pearson and Allen M. Poteshman(2005), **Stock price clustering on option expiration dates**, *Journal of Financial Economics*78(1),49–87. https://doi.org/10.1016/j.jfineco.2004.08.005 . Journal identity/authors/pages confirmed at https://api.crossref.org/works/10.1016/j.jfineco.2004.08.005 ; abstract of2004 author working-paper version confirmed in Crossref at DOI https://doi.org/10.2139/ssrn.519044 . Full journal paper not retrieved; use only abstract-supported qualitative findings, not remembered sample details/statistics.
2. Benjamin Golez and Jens Carsten Jackwerth(2012), **Pinning in the S&P500 futures**, *Journal of Financial Economics*106(3),566–585. https://doi.org/10.1016/j.jfineco.2012.06.010 . Journal metadata confirmed in Crossref title search;2010 author abstract confirmed at https://doi.org/10.2139/ssrn.1664261 via Crossref. The abstract explicitly states pinning *and anti-cross-pinning*. Direct SSRN page403; fulltext not retrieved. Do not cite the superficially similar DOI ending06.005, which is a different paper.
3. Marco Avellaneda and Michael D. Lipkin(2003), **A market-induced mechanism for stock pinning**, *Quantitative Finance*3(6),417–425. https://doi.org/10.1088/1469-7688/3/6/301 . Journal metadata and working-paper abstract https://doi.org/10.2139/ssrn.458020 confirmed in Crossref. Model mechanism only; not a calibrated NQ pin probability. DOI ending/305 is a different paper and must not be used.
4. Andrea Barbon and Andrea Buraschi(2020 Crossref working-paper registration), **Gamma Fragility**, SSRN working paper3725454. https://doi.org/10.2139/ssrn.3725454 . Author names and full abstract opened via Crossref search. The abstract reports negative(positive) ex-ante gamma interacting with illiquidity explains intraday momentum(reversal), stronger in less-liquid underlying stocks. This is not an NQ-specific study. Version/publication status beyond the verified working-paper record was not established; do not label it peer reviewed or cite an invented journal.
5. Mandy Xu(2023-09-08), **Much Ado About0DTEs — Evaluating the Market Impact of SPX0DTE Options**, Cboe Insights, full article opened. https://www.cboe.com/insights/posts/volatility-insights-evaluating-the-market-impact-of-spx-0-dte-options/ . Primary exchange analysis, not peer reviewed and not a current2026 positioning report.
6. CME Group(undated,current specifications), **E-mini Nasdaq-100 Futures Contract Specs**, **Micro E-mini Nasdaq-100 Futures Contract Specs**, **E-mini S&P500 Futures Contract Specs**. https://www.cmegroup.com/markets/equities/nasdaq/e-mini-nasdaq-100.contractSpecs.html ; https://www.cmegroup.com/markets/equities/nasdaq/micro-e-mini-nasdaq-100.contractSpecs.html ; https://www.cmegroup.com/markets/equities/sp/e-mini-sandp500.contractSpecs.html . Pages plus actual specification API read; API links above.
7. CME Group(current), **Rulebook, Chapter359: E-mini Nasdaq-100 Index Futures**, especially35901,35902.G,35903. Full PDF read via pdftotext. https://www.cmegroup.com/rulebook/CME/IV/350/359/359.pdf . Final SOQ, business-day exceptions and contract multiplier are authoritative rules.
8. CME Group(current), **Nasdaq-100 settlement procedures**, full body opened from official product-spec link https://www.cmegroup.com/confluence/display/EPICSANDBOX/Nasdaq-100 which redirects to https://cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457222172/Nasdaq-100 . Section Normal Daily Settlement Procedure, Lead Month Tier1–3; Final Settlement.
9. CME Group(current), **Equity Index Roll Dates**, full page read. https://www.cmegroup.com/trading/equity-index/rolldates.html . Monday convention, voluntary timing and2026 table verified.
10. CME Group(current), **Calculating Fair Value**, full page read. https://www.cmegroup.com/trading/equity-index/fairvalue.html . Financing, dividends, expiry and actual supply/demand basis deviations.
11. CME Group(current), **Globex Trading Hours and Holiday Schedules**, full page read. https://www.cmegroup.com/trading-hours.html .2026 product-specific schedules subject to change; do not replace them with the cash calendar.
12. Nasdaq(current2026), **U.S. Stock Market Holiday Schedule / Trading Hours**, full page read. https://www.nasdaq.com/market-activity/stock-market-holiday-schedule . Weekday09:30–16:00ET cash hours,2026 closures and13:00ET early closes.
13. Cboe Global Indices(current, PDF contains March23,2026 amendment), **Cboe Selected Broad-Based Index, Equity and ETF Volatility Indices: Methodology**, full PDF read. Link discovered on official VXN dashboard: https://cdn-api.cboe.com/api/global/us_indices/governance/Volatility_Index_Methodology_Selected_Broad_Based_Index_Equity_and_ETF_Volatility_Indices.pdf . Sections1.1,2.1 and VXN row:30-day target from NDX/NDXP, Nasdaq PHLX options venue, VXN dissemination09:31–16:15ET. https://www.cboe.com/us/indices/dashboard/vxn/ . Does not assert futures1-day forecast accuracy.
14. Cboe Global Indices, **VXN daily historical prices**, retrieved2026-10-17. https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv redirects officially to https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv . Last observation2026-10-16. CSV was read and final observations verified.
15. Cboe Global Indices, **VIX / VIX3M daily historical prices**, retrieved2026-10-17. https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv and https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX3M_History.csv (same official cdn-api redirects). Last observations2026-10-16.
16. U.S. Bureau of Labor Statistics(2026-10-14), **Consumer Price Index — September2026**, USDL26-1574. Full release opened. https://www.bls.gov/news.release/cpi.nr0.htm . Mutable current-release URL, observation and publication date explicitly recorded.
17. U.S. Bureau of Economic Analysis(2026-09-30), **Personal Income and Outlays, August2026**, BEA26-43. Full release opened. https://www.bea.gov/news/2026/personal-income-and-outlays-august-2026 . Includes next release date.
18. U.S. Bureau of Labor Statistics(2026-10-02), **The Employment Situation — September2026**, USDL26-1549. Full release opened. https://www.bls.gov/news.release/empsit.nr0.htm . Mutable release URL, date explicitly recorded.
19. Board of Governors, via Federal Reserve Bank of St.Louis FRED, **Market Yield on U.S. Treasury Securities at10-Year Constant Maturity, Quoted on an Investment Basis, Inflation-Indexed(DFII10)**, latest observed2026-10-15,2.78%. https://fred.stlouisfed.org/series/DFII10 . Page's actual observation date/value and updated timestamp read.
20. Board of Governors, via FRED, **Federal Funds Effective Rate(DFF)**, latest observed2026-10-15,3.88%. https://fred.stlouisfed.org/series/DFF . Actual observation/date read; not a policy-target-range source.

No forums, social media, blogs, community TradingView ideas or invented hit rates were used. Academics with only an abstract accessed are explicitly marked above. A DOI/title mismatch was resolved rather than cited from memory.

### Additional MES verification

CME Group, *Micro E-mini S&P 500 Futures Contract Specs*: https://www.cmegroup.com/markets/equities/sp/micro-e-mini-sandp-500.contractSpecs.html . Its official specification API was opened: https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/8667 . Contract unit **$5 × S&P 500 index**, outright tick **0.25 points = $1.25**; calendar-spread tick differs (**0.05 points = $0.25**). Globex 18:00–17:00 ET and maintenance 17:00–18:00 ET. These support the MES risk-budget example; no trading-edge claim follows.


# Annexe C — documentation Pine vérifiée

# Pine Script platform: live official verification

Verified by HTTPS GET against official TradingView pages on 2026-10-17. Every URL below returned HTTP 200. HTML was read locally; these are documentation checks, **not compilation or TradingView execution tests**.

## Version and new capabilities

- Official migration guide: https://www.tradingview.com/pine-script-docs/migration-guides/to-pine-version-6/
- Current release notes: https://www.tradingview.com/pine-script-docs/release-notes/
- The current manual and examples use `//@version=6`. Release notes contain September 2026 updates, so older statements that footprint data is unavailable in Pine are now obsolete.
- Release notes, January 2026: “We’ve added a new request.footprint() function and two new data types, footprint and volume_row.”
- Important v6 syntax rule: “The history-referencing operator [] can no longer be used directly on fields of user-defined types.” Use `(myObject[1]).field`, or assign the field to a scalar variable and then use `scalar[1]`.

## Requests, common 1-minute clock, and limitations

Official chapter: https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/

Verified statements:

1. Every unique `request.*()` request evaluates an expression over the requested symbol/timeframe dataset.
2. Signature:
   ```pine
   request.security_lower_tf(symbol, timeframe, expression, ignore_invalid_symbol, currency, ignore_invalid_timeframe, calc_bars_count) → array<type>
   ```
3. Exact passage: “This function requests data only from timeframes that are lower than or equal to the chart’s timeframe (timeframe.period).” Therefore, a request for `"1"` is documented as supported on each of 1m, 5m, 10m, 15m, 1h, and 4h. A separate security request for the equal-1m case is not required by this documentation. **Its actual equal-timeframe realtime behavior still needs a TradingView test.**
4. The arrays contain values “sorted in ascending order based on each intrabar’s timestamp.”
5. A tuple expression, including a function returning a tuple, produces a tuple of arrays. Example: `[open, high, low, close]` produces four arrays.
6. `request.security()` on a lower timeframe retrieves only a single intrabar per chart bar. It is unsuitable for preserving every minute’s sequential event history on a 4h chart.
7. `request.security_lower_tf()` accepts most requestable expression types, excluding **direct references to collections and mutable variables**. A user function with internal state and a scalar/tuple/UDT result is the appropriate expression form; actual syntax must still be compiled.
8. `request.security()` can return UDT IDs with fundamental fields, chart points, eligible collections, or eligible nested UDTs. The lower-timeframe chapter also demonstrates UDT results (`array<Prices>`); UDT wrappers permit collections to be returned, but the documentation calls the collection technique advanced and recommends simpler alternatives where possible.
9. A scalar-only snapshot UDT is a useful alternative to a very large tuple. Return a **new snapshot object** each source bar; do not return and repeatedly mutate the same object as historical records. Keep growing profile arrays internal to the source engine rather than returning a fresh large collection at every minute.
10. Empty arrays are possible outside the retrieved source coverage. Always guard `array.get`, `first`, and `last` with a size test. Missing minutes and source gaps are possible, so do not assume `chart_minutes` equals array size.
11. Minor retrospective changes remain possible even with `request.security_lower_tf()`: exact excerpt, “it’s still possible in some cases for minor repainting to occur due to data differences from the provider”. Documentation explains that historical and realtime feeds can differ, providers can revise data, and races can occur between feeds.
12. `barmerge.lookahead_on` with an unoffset lower-timeframe `request.security` expression does not solve this. On history it can select a first intrabar, while realtime selection differs.

### Recommended architecture (engineering inference, not a tested TradingView result)

- One source engine operates entirely in a fixed 1-minute context; use the same exchange symbol/session settings and timezone inputs on every chart.
- Within that engine, update session VWAP, profile histograms, minute-based ranges, proxy volume flow, readiness, and event state. Derive time periods from source timestamps, **never from the display chart bar count**. Source readiness must be based on complete source sessions and coverage checks.
- Request a scalar-only snapshot UDT or modest tuple using one `request.security_lower_tf` call with `"1"` and an explicit conservative `calc_bars_count = 100000`.
- Include each minute’s source-open timestamp, source-close timestamp, sequence/session identifier, readiness flags, and event timestamp in its snapshot.
- On every chart execution, inspect the returned snapshots in chronological order. Only consume a source snapshot whose source close is no later than the actual execution clock. Preserve the last known completed snapshot if the current array contains no completed minute. Do not use `barstate.isconfirmed` inside `request.security` to establish source confirmation (see below).
- Display the latest completed snapshot; record all relevant events, not only the last array element. Historical 4h bars contain many source observations; attach event drawings to **source timestamps** with `xloc.bar_time`.
- Reset bounded state on source session boundaries, reject the first incomplete source session, and flag unavailable prior profiles. Across charts, equality can only be promised for the same completed source timestamp after the **same complete warmup and available underlying data**. Different plan/history coverage can affect initial conditions.
- Display-chart plots have one value per display bar. Identical source-clock values do not imply identical-looking line sampling across chart timeframes, nor that a complete historical 4h bar’s contents were all known at its opening.
- Do not claim absolute freedom from provider revisions or exchange data corrections.

## Footprints, volume delta, and unsupported data assumptions

Official request documentation:
https://www.tradingview.com/pine-script-docs/concepts/other-timeframes-and-data/

Official type documentation:
https://www.tradingview.com/pine-script-docs/language/type-system/

Verified `request.footprint()` capabilities:

- Signature: `request.footprint(ticks_per_row, va_percent, imbalance_percent) → series footprint`.
- Provides footprint rows, total/buy/sell volume, delta, POC, VAH, VAL, and diagonal imbalance checks.
- “Volume footprints are available exclusively to users who have a Premium or Ultimate plan.” Lower-tier accounts cannot use scripts that request them.
- At most one unique footprint request. A `request.security()`/`lower_tf` expression dependent on footprint data counts toward the unique-footprint limit. Adding a chart-local footprint call and a separately requested footprint context can raise a runtime error.
- Data can be `na` even with a permitted subscription.
- Crucial meaning: the official description says footprints categorize lower-timeframe volume as buy/upward or sell/downward **based on intrabar price action**. These labels must not be represented as authenticated exchange aggressor-side trades or a complete Level 2 order book.
- For a broadly compatible deliverable, use an explicitly labelled 1m price-direction volume proxy by default. A separate footprint edition is possible for eligible users; do not include an unsupported hidden footprint request in a general-plan script.

Official Volume Delta description (canonical article ID; the arbitrary slug does not select its identity):
https://www.tradingview.com/support/solutions/43000725057/

Exact important description: “The Volume Delta indicator uses intrabar volume and price fluctuations to estimate the difference (delta) between buying and selling pressure within each chart bar”. It classifies close > open as positive, close < open as negative; for a doji it compares with the prior intrabar close; when both are equal it preserves the prior sign. A 1m implementation of this rule is a **directional-volume proxy**, not an exact replica of native subminute delta.

No documented `request.*()` API in the current manual provides a full options chain, dealer positioning inventory, or account-level gamma exposure. Option symbols, manually supplied levels, externally calculated reference values, and futures-derived proxies are different data products. Do not imply an automatically fetched full options chain, measured dealer gamma/GEX, true bid/ask aggressor delta, or Level 2 DOM without an actual supported data source.

## Confirmation, rollback, and alerts

Official bar states:
https://www.tradingview.com/pine-script-docs/concepts/bar-states/

- `barstate.isconfirmed` is true on every historical bar and on the final closing update of a realtime chart bar.
- Exact warning: “barstate.isconfirmed will not work when used in a request.security() call.” Do not confuse parent-chart confirmation with confirmation of a requested 1m source.

Official execution model:
https://www.tradingview.com/pine-script-docs/language/execution-model/

- Indicators recalculate with realtime updates; rollback resets ordinary state to its previous committed bar state before each new update.
- `varip` can retain state between realtime ticks; that also means intrabar behavior is not historically reconstructible after reload unless restricted to deduplicating already closed source timestamps.
- A realtime parent-bar scan can be redone from the parent bar’s committed initial state using the ordered completed-minute array. For event alerts, a small `varip` last-alert source timestamp can suppress duplicate alerts within the open parent bar, but should never be used to manufacture unreplayable signal calculations.

Official alerts:
https://www.tradingview.com/pine-script-docs/concepts/alerts/

- “Alerts only trigger in the realtime bar.” No historical backfill of alert notifications.
- A script supplies alert events; the user must create the running alert in the TradingView UI.
- The alert server stores a snapshot of the script, inputs, symbol, and chart timeframe. Changes require recreating the alert.
- `alert.freq_once_per_bar_close` means the **chart bar** closing update. It would delay a minute-source alert until the display bar’s close, potentially 4h. That should not be marketed as timeframe-independent realtime timing.
- For minute-close source events on a higher chart timeframe: inspect closed source snapshots, use `alert.freq_all` and source-timestamp deduplication, and explicitly test availability/timing in TradingView. TradingView cannot emit anything without a market update; exact wall-clock delivery is not guaranteed.
- If loading a script halfway through a 4h bar, choose and document a freshness rule so it does not alert for every older event inside that open bar. Alert notification traffic is not the signal history.

## Budgets to respect

Official limitations:
https://www.tradingview.com/pine-script-docs/writing/limitations/

- 40 unique `request.*()` calls ordinarily; 64 for Ultimate. Identical repeated requests normally reuse an existing request.
- All non-professional plans (Basic, Essential, Plus, Premium): up to 100,000 LTF bars; Expert: 125,000; Ultimate: 200,000. Explicit `calc_bars_count` controls requested history, within plan/dataset limits. It does not make inaccessible history available.
- Lower timeframe chart coverage depends on actual minute counts. A 100,000-minute budget covers approximately 416 full 4h bars in a nonstop market, and more parent bars when source minutes are missing.
- All tuple results across all `request.*()` calls together: at most 127 elements. UDT fields provide the documented alternative when larger structured snapshots are necessary.
- Up to 64 plot counts. `alertcondition`, series colors and some multi-series plots can consume extra counts.
- Maximum IDs: 500 lines, 500 boxes, 500 labels, 100 polylines. Existing IDs count even if coordinates are `na`. Reuse/delete objects instead of creating unbounded objects.
- Each loop is capped at 500 ms per bar; total script execution is capped at 20 s for Basic and 40 s for other plans.
- Each collection has a maximum of 100,000 elements.
- Use fixed-size histograms, bounded event history, bounded object pools, and avoid scanning thousands of bins every source minute. Performance and object budgets must be tested in TradingView on the longest target timeframe.

## Validation boundaries

This environment has no TradingView Pine compiler or live paid TradingView feed. Official-document checks and local mirror tests can validate definitions, boundedness, chronological replay, and deterministic aggregation. They cannot prove that the Pine file compiles, fits TradingView runtime limits, has equal 1m request realtime behavior, or emits alerts at the intended time. Keep compilation, runtime, data entitlement, and six-timeframe timestamp comparisons as explicit remaining acceptance checks in TradingView.

## Continuous futures: adjustment and rollover (additional official reference check)

Official reference URLs:

- https://www.tradingview.com/pine-script-reference/v6/#fun_ticker.modify
- https://www.tradingview.com/pine-script-reference/v6/#fun_ticker.new
- https://www.tradingview.com/pine-script-reference/v6/#var_syminfo.current_contract

The reference page is dynamically rendered. Its current official reference payload was fetched successfully from the TradingView static origin, as loaded by that page:
https://static.tradingview.com/static/bundles/11967.3c92723cdb229aeaa95a.js

The payload declares exactly:
```text
name:"syminfo.current_contract",type:"simple string"
```
Its official English definition is: “The ticker identifier of the underlying contract, if the current symbol is a continuous futures contract; na otherwise.”

**Critical implication:** `syminfo.current_contract` is a **simple** value, not a historical `series string`. It is not a documented source of per-bar historical contract identifiers. Comparing this value to its history in a continuous NQ1! source engine does not reliably detect historical rollover. It can identify/display the current underlying contract. Do not claim automatic exact historical rollover detection from this variable.

Supported named options:
```pine
sourceTicker = ticker.modify(syminfo.tickerid,
     backadjustment = backadjustment.off,
     settlement_as_close = settlement_as_close.off)
```

- `backadjustment`: `.on`, `.off`, `.inherit`; controls backadjustment of past contract data for eligible continuous futures.
- `settlement_as_close`: `.on`, `.off`, `.inherit`; actual close versus settlement **only on 1D and higher** data. It has no minute-close settlement effect.
- Explicit `.off` fixes a reproducible source policy but does not remove contract rollover gaps.
- With unadjusted NQ1!, prior-session price references can straddle different contracts. Recommended exact handling is dated contract symbols plus an explicit roll/reset policy, or user-provided historical roll/reset timestamps. Gap-based detection may be a conservative heuristic; ordinary overnight gaps and roll gaps are not uniquely distinguishable from OHLCV alone. Mark such a detector and its false-positive/false-negative limitations explicitly.
- Continuous-series backadjustment can change historical price levels after rollover; values previously displayed can therefore change after reload even when signal code itself is causal.

### Returning an offset source snapshot

The current official `request.security_lower_tf` reference explicitly accepts “a function call that does not use Pine Script® drawings, an object, or a tuple of expressions.” Collections are permitted only inside object fields. The manual gives an `array<Prices>` result example, so returning `array<SourceSnapshot>` with fundamental scalar fields is a documented pattern.

A one-minute causal lag can be constructed by first calculating every scalar series in the source engine and constructing `SourceSnapshot.new(sourceTime[1], sourceCloseTime[1], scalar1[1], ...)`. A prior snapshot object may alternatively be referenced as `snapshot[1]`, guarding `na` before reading its fields. Do **not** write `snapshot.field[1]` in v6. If deliberate offsetting is used, carry the lagged source timestamp with all the lagged values and document actual delivery latency. Whether the equal-timeframe lower_tf call provides the forming 1m object or only a closed one in realtime remains a specific runtime acceptance test, so do not promise tick-exact arrival from documentation alone.

### Selected safe policy for present-day continuous-chart use

If the chart is continuous and `syminfo.current_contract` is available, using that **simple ticker identifier as a fixed requested source symbol** is consistent with the documented `request.*` symbol contract. It requests the current dated contract's own price/volume history rather than concatenating old front contracts. `ticker.modify` can apply an explicit source session and adjustment policy. Keep a user override for an explicit dated contract identifier, and fall back conservatively if metadata is unavailable.

This solves a present-day reference-mixing problem, with these boundaries:

- It intentionally does **not** recreate the then-front contract across old continuous-chart history. In historical replay crossing an old roll, the user must supply the dated contract appropriate to that replay interval.
- Latest-zone display avoids plotting current-contract historical prices as though they were the continuous chart's then-front historical levels.
- A fixed current dated contract can have sparse volume earlier in its life. Twenty session boundaries are not alone proof of twenty liquid, complete source sessions. Validate minute coverage and positive volume; report missing/thin source history.
- Source contract or input changes require TradingView alert recreation. Automatic exact live alert rollover handling must not be claimed without runtime testing.
