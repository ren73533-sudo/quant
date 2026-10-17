# Session reference zones

Indicateur Pine Script v6 pour NQ/MNQ et ES/MES, sur 1m/5m/10m/15m/1h/4h.

- `key_zones.pine` : script complet à copier dans Pine Editor.
- `AUDIT.md` : audit du code final, recherche vérifiée, contexte au 17 octobre 2026, références et limites.
- `GUIDE.md` : installation, réglages, routine quotidienne et réception TradingView.
- `validation/README.md` : comparaison hors ligne de zones contre témoins aléatoires appariés.
- `research/` : notes sources ; le corps principal de l'audit décrit l'implémentation finale.

Contrôles locaux : `python3 -m unittest discover -s validation -v` (Python 3.10+, bibliothèque standard seulement).

24 tests synthétiques passent. Aucun backtest NQ n'est fourni ; aucune probabilité de rebond n'est estimée. Le code Pine est relu contre la documentation officielle mais ne peut pas être compilé dans cet environnement. La compilation, les droits de données, l'affichage et les délais d'alertes sur TradingView restent à vérifier selon le guide.
