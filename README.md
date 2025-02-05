# Projektarbeit Modul 319: Applikationen entwerfen und implementieren

## Kurrzfassung
Meine Projektarbeit im Modul 319: Applikationen entwerfen und implementieren\
**Note : 5.0** (Dokumentation, Zeitplan, Präsentation, Prozesszeichnung)\
**Schule : [GBS St.Gallen](https://www.gbssg.ch/)**\
**Ort : Schweiz 🇨🇭**, Kanton Graubünden

## Einleitung
Programmierteil für Projektarbeit Weiterbildung im Modul 319: Applikationen entwerfen und implementieren\
Im Rahmen des Schulprojekts wurde ein Python-Skript entwickelt, das einen bestimmten Prozess zur Lösung eines schulischen Problems unterstützt. Ziel war es, mit Hilfe dieses Skripts den Ablauf zu automatisieren und die Effizienz des Prozesses zu steigern. Das Skript stellt ein praktisches Beispiel für den Einsatz von Programmiertools in schulischen Kontexten dar.

## Flowchart
![Ablaufgrafik](img/flowchart.png)

## Start des Projektes
Befehle für den Start des Projekts.\
1. Erstellung einer virtuellen Umgebung: 
```bash
python3 -m venv venv
```
2. Installation der Module in der virtuellen Umgebung
```bash
source venv/bin/activate && pip install -r requirements.txt
```
3. Starten des Webservers
```bash
uvicorn app:app --reload 
```
