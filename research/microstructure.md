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
