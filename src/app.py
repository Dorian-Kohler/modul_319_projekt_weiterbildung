"""
    Verwendete Bibliotheken
"""
# Warum FastAPI als Web-Bibliothek für Python?
# Grundsätzlich gibt es für kleinere Web-Projekte die Bibliotheken Flask, Django und FastAPI.
# Django erstellt für ein solch kleines Projekt zu viel Code, der nicht benötigt wird. Flask war nicht der Favorit meines Betreuers. FastAPI ist zudem moderner.
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
import numpy as np
import uuid, requests
from typing import Optional

MAILGUN_KEY = # "insert your mailgun key"

"""
    Initialisierung der FastAPI-App
"""

# Web-Applikation wird initialisiert
app = FastAPI()
# Legt fest, wo die HTML-Dateien sind
templates = Jinja2Templates(directory="templates")

"""
    Excel-Dateien die im Projekt als Datenbank verwendet werden
"""

# Datei-Pfade der Excel-"Datenbank"
INPUT_FILE = "data.xlsx"
OUTPUT_FILE = "output_data.xlsx"

"""
    Funktionen zum Lesen und Schreiben der Excel-Dateien.
"""

# Lade die Daten aus der Excel-Datei
def load_data():
    df = pd.read_excel(INPUT_FILE)
    names = df['Name'].unique().tolist() # Nimm Alle einzigartigen Werte 1x in der Spalte Name
    # Was passiert, wenn es Lehrpersonen mit exakt dem gleichen Namen gibt?
    weiterbildungen = df['Weiterbildung'].unique().tolist() # Nimm Alle einzigartigen Werte 1x in der Spalte Weiterbildung
    name_df = df['Name'] # Nimm Alle einzigartigen Werte 1x in der Spalte Fächer
    weiterbildungen_df = df['Weiterbildung']
    return df, names, weiterbildungen, name_df, weiterbildungen_df # gebe die Variablen zurück

def load_entries():
    df = pd.read_excel(OUTPUT_FILE)
    return df # gebe die Variablen zurück

# Hilfsfunktion: Speichere Daten in INPUT_FILE
def save_data(df, file):
    df.to_excel(file, index=False)

"""
    Beginn Webseite: Funktionen der Routen für Formular Lehrperson
    - /
    - /check-wb-necessity
    - /submit
"""

# Funktion zum Versand von E-Mails via Mailgun
# ACHTUNG: aktuell kann nur d-kohler@bluewin.ch E-Mails empfangen. Weitere E-Mail Adressen müssen im Admin-Bereich von Mailgun aktiviert werden (Authorized Recipients).
def send_simple_message(to :list, subject, text):
  	return requests.post(
  		# "insert correct mailgun server",
  		auth=("api", MAILGUN_KEY),
  		data={"from": # "insert correct mailgun email adress",
  			"to": to,
  			"subject": subject,
  			"text": text})

# HAUPT-Einstiegspunkt
# Startseite mit Formular anzeigen für Lehrperson
@app.get("/", response_class=HTMLResponse) # liefere HTML zurück
async def form(request: Request): # Definition der Formularklasse
    _, names, weiterbildungen, _, _ = load_data() # Lade in die drei Variablen names, weiterbildungen und faecher die Daten aus dem Excel INPUT_FILE
    return templates.TemplateResponse("form.html", { # Gib form.html zurück und gib die Variabeln auch ins HTML mit
        "request": request, # wird von FastAPI benötigt
        "names": names,
        "weiterbildungen": weiterbildungen
    })

# Route für HTMX, um die zusätzlichen Felder anzuzeigen
@app.get("/check-wb-necessity", response_class=HTMLResponse)
async def check_wb_necessity(request: Request, weiterbildung: str = None, faecher: list = None):
    if weiterbildung or faecher:
        return templates.TemplateResponse("wb_options.html", {
            "request": request
        })
    return HTMLResponse("")

# Formular absenden und speichern
@app.post("/submit")
async def submit_form(
    request: Request,
    name: str = Form(...),
    vorgaben: str = Form(...),
    weiterbildung: str = Form(...),
    abteilung: str = Form(...),
    pensum: str = Form(...),
    anbieter: str = Form(...),
    bezeichnung: str = Form(...),
    inhalt: str = Form(...),
    daten: str = Form(...),
    TagemitUnterricht: str = Form(...),
    AnzahlbetroffeneLektionen: str = Form(...),
    AnzahlTageohneUnterricht: str = Form(...),
    Nutzen: str = Form(...),
    Kurskosten: str = Form(...),
    GesamtkosteninCHF: str = Form(...),
    Spesen: str = Form(...),
    email: str = Form(...)
):
    # Erstellen eines neuen DataFrames für den Eintrag
    new_entry = pd.DataFrame([{
        "Name": name,
        "Vorgaben": vorgaben,
        "Weiterbildung": weiterbildung,
        "Abteilung": abteilung,
        "aktuelles Pensum": pensum,
        "Kursanbieter": anbieter,
        "Kursbezeichnung": bezeichnung,
        "Kursinhalt": inhalt,
        "Kursdaten": daten,
        "Anzahl Tage mit Unterricht": TagemitUnterricht,
        "Anzahl betroffene Lektionen": AnzahlbetroffeneLektionen, 
        "Anzahl Tage ohne Unterricht": AnzahlTageohneUnterricht,
        "Nutzen für die Tätigkeit als Lehrperson": Nutzen,
        "Kurskosten": Kurskosten,
        "Gesamtkosten in CHF": GesamtkosteninCHF,
        "Spesen (Reise, Unterkunft, Verpflegung)": Spesen,
        "Email": email,
        "Datum Beantragt": pd.Timestamp.now(),
        "Bewilligt?": "in Prüfung",
        "Datum Entscheid": "",
        "secret": uuid.uuid4(),
        "Prorektor Bewilligt?": False
    }])

    try:
        # Falls die Datei bereits existiert, laden wir sie und hängen die neuen Daten an
        existing_data = pd.read_excel(OUTPUT_FILE)
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
    except FileNotFoundError:
        # Falls die Datei nicht existiert, starten wir sie nur mit den neuen Daten
        updated_data = new_entry
    
    # Speichert die Daten in `output_data.xlsx` und überschreibt sie nicht
    updated_data.to_excel(OUTPUT_FILE, index=False)

    send_simple_message([email], "Beantragung einer individuellen Weiterbildung", f"Guten Tag {name},\nwir haben Ihren Antrag erhalten und werden diesen schnellstmöglich bearbeiten. Den Status zum Antrag sehen sie unter folgendenm Link: http://localhost:8000/status/{new_entry.secret.values[0]}")
    
    return templates.TemplateResponse("bestaetigung.html", {
        "request": request,
        "message": "Vielen Dank für die Beantragung einer individuellen Weiterbildung",
        "link_excel": "/status/" + str(new_entry.secret.values[0]),  # Link zur Ansicht der Excel-Daten
        "link_new_form": "/"  # Link zum neuen Formular
    })


"""
    Webseite: Funktion der Routen status (Status der Prüfung für Lehrperson)
    - /status
"""

# Excel-Daten anzeigen (nur das Feld "Bewilligt?")
@app.get("/status/{secret}", response_class=HTMLResponse)
async def view_excel(request: Request, secret: str):
    try:
        df = pd.read_excel(OUTPUT_FILE) # Excel Datei OUTPUT_FILE wird eingelesen in ein panda DataFrame
        df.replace({np.nan: None}, inplace=True)
        bewilligt_data = df[df["secret"] == secret][["Name", "Weiterbildung", "Bewilligt?", "Datum Entscheid"]].to_dict(orient="records")  # Nur Name und Bewilligt? von spezifischem secret
    except FileNotFoundError:
        bewilligt_data = []

    return templates.TemplateResponse("view_excel.html", {
        "request": request,
        "data": bewilligt_data
    })

"""
    Webseite: Funktion der Routen für Admin
    - /admin/* (CRUD) -> add, update, delete
    - /admin/statistik
    - /admin/antraege
"""

# CRUD-Admin-Seite
@app.get("/admin", response_class=HTMLResponse) 
async def admin(request: Request):
    df, names, weiterbildungen, _, _ = load_data()
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "data": df.reset_index().to_dict(orient="records"),
        "names": names,
        "weiterbildungen": weiterbildungen,
    })


# Eintrag hinzufügen
@app.post("/admin/add")
async def add_entry(name: Optional[str] = Form(None), weiterbildung: Optional[str] = Form(None)):
    df, _, _, name_tabelle, weiterbildung_tabelle = load_data()
    # Erstelle leeres DataFrame, um neue Einträge schrittweise hinzuzufügen
    new_entry = pd.DataFrame()

    # Füge Namen zur entsprechenden Spalte hinzu, wenn angegeben
    if name:
        if "Name" not in df.columns:
            df["Name"] = pd.Series(dtype=str)  # Falls die Spalte "Name" fehlt
        new_entry["Name"] = [name]

    # Füge Weiterbildung zur entsprechenden Spalte hinzu, wenn angegeben
    if weiterbildung:
        if "Weiterbildung" not in df.columns:
            df["Weiterbildung"] = pd.Series(dtype=str)  # Falls die Spalte "Weiterbildung" fehlt
        new_entry["Weiterbildung"] = [weiterbildung]

    # Kombiniere die vorhandenen Daten mit den neuen Einträgen
    updated_data = pd.concat([df, new_entry], ignore_index=True)
    
    save_data(updated_data, INPUT_FILE)
    return RedirectResponse("/admin", status_code=303)


# Eintrag aktualisieren
@app.post("/admin/update")
async def update_entry(index: int = Form(...), name: Optional[str] = Form(None), weiterbildung: Optional[str] = Form(None)):
    df, _, _, _, _ = load_data()
    if name:
        df.at[index, "Name"] = name
    if weiterbildung:
        df.at[index, "Weiterbildung"] = weiterbildung
    save_data(df, INPUT_FILE)
    return RedirectResponse("/admin", status_code=303)


# Eintrag löschen
@app.post("/admin/delete")
async def delete_entry(index: int = Form(...)):
    df, _, _, _, _ = load_data()
    df = df.drop(index)
    df.reset_index(drop=True, inplace=True)
    save_data(df, INPUT_FILE)
    return RedirectResponse("/admin", status_code=303)


# CRUD-Admin-Seite
@app.get("/admin/statistik", response_class=HTMLResponse) 
async def admin_statistik(request: Request):
    df = load_entries()
    df.replace({np.nan: None}, inplace=True)
    return templates.TemplateResponse("statistik.html", {
        "request": request,
        "data": df.to_dict(orient="records"),
})     
# Admin-Route für Anträge
@app.get("/admin/antraege", response_class=HTMLResponse)
async def admin_antraege(request: Request):
    
    try:
        df = pd.read_excel(OUTPUT_FILE) # Excel Datei OUTPUT_FILE wird eingelesen in ein panda DataFrame
        # in Variable data wird das DataFrame mit den folgenden Spalten gespeichert
        # data = df[["Name", "Weiterbildung", "Bewilligt?", "secret", "Datum Entscheid"]]
        # Abfragen im Excel basierend auf Kurskosten
        # Ersetze Panda NaN und Panda NaT jeweils mit Python None  
        below_thousand = df[df["Gesamtkosten in CHF"] <= 1000]
        below_thousand.replace({np.nan: None}, inplace=True)

        between_thousand = df[(df["Gesamtkosten in CHF"] >= 1001) & (df["Prorektor Bewilligt?"] == False)]
        between_thousand.replace({np.nan: None}, inplace=True)

        above_thousand = df[(df["Gesamtkosten in CHF"] >= 5000) & (df["Prorektor Bewilligt?"] == True)]
        above_thousand.replace({np.nan: None}, inplace=True)

        below_thousand = below_thousand.reset_index().to_dict(orient="records")
        between_thousand = between_thousand.reset_index().to_dict(orient="records")
        above_thousand = above_thousand.reset_index().to_dict(orient="records")

        # Wandle das DataFrame zu einer Liste um (Dictionary)
        # data = data.to_dict(orient="records")
    except FileNotFoundError:
        below_thousand = []
        between_thousand = []
        above_thousand = []

    return templates.TemplateResponse("antraege.html", {
        "request": request,
        "data_below":  below_thousand,
        "data_between": between_thousand,
        "data_rektor": above_thousand
    })
    

# Aktualisieren der Anträge
@app.post("/admin/antraege/update")
async def admin_antraege_update_confirmation(index: int = Form(...), bewilligt: str = Form(...)):
    df = load_entries()
    if (df.at[index, "Gesamtkosten in CHF"] < 5000):
        df.at[index, "Bewilligt?"] = bewilligt  # "Bewilligt?"-Spalte aktualisieren
    elif (df.at[index, "Prorektor Bewilligt?"] == True):
        df.at[index, "Bewilligt?"] = bewilligt  # "Bewilligt?"-Spalte aktualisieren, da Prorektor schon bewilligt hat
    else:
        df.at[index, "Prorektor Bewilligt?"] = True # Prorektor Bewilligung
    df.at[index, "Datum Entscheid"] = pd.Timestamp.now()
    save_data(df, OUTPUT_FILE)

    if (df.at[index, "Gesamtkosten in CHF"] >= 5000 ):
        if (df.at[index, "Bewilligt?"] != "in Prüfung" and df.at[index, "Prorektor Bewilligt?"] == True):
            send_simple_message([df.at[index, "Email"]], "Entscheid Ihrer individuellen Weiterbildung", f"Guten Tag {df.at[index, 'Name']},\nIhr Antrag wurde {bewilligt.lower()}. Der Link zum Antrag lautet: http://localhost:8000/status/{df.at[index, 'secret']}")
    else:
        if (df.at[index, "Bewilligt?"] != "in Prüfung"):
            send_simple_message([df.at[index, "Email"]], "Entscheid Ihrer individuellen Weiterbildung", f"Guten Tag {df.at[index, 'Name']},\nIhr Antrag wurde {bewilligt.lower()}. Der Link zum Antrag lautet: http://localhost:8000/status/{df.at[index, 'secret']}")

    return RedirectResponse("/admin/antraege/", status_code=303)