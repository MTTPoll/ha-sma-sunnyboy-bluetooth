# ☀️🔵 SMA Sunny Boy Bluetooth Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5.svg)](https://www.home-assistant.io/)
[![GitHub release](https://img.shields.io/github/v/release/mttpoll/ha-sma-sunnyboy-bluetooth?display_name=tag)](https://github.com/mttpoll/ha-sma-sunnyboy-bluetooth/releases)
[![GitHub issues](https://img.shields.io/github/issues/mttpoll/ha-sma-sunnyboy-bluetooth)](https://github.com/mttpoll/ha-sma-sunnyboy-bluetooth/issues)

**SMA Sunny Boy Bluetooth Home Assistant Integration** is a Home Assistant custom integration for legacy **SMA Sunny Boy** and **SMA Sunny Tripower** inverters using native Bluetooth communication.

It connects directly to your inverter using SMA Bluetooth RFCOMM communication and does **not require SBFspot**, Sunny Explorer or any external software.

> Currently tested with the **SMA Sunny Boy 4000TL-20**.
> Other SMA Bluetooth inverters may also work.

---

## Language

* [English](#english)
* [Deutsch](#deutsch)

---

# English

## ✨ Features

SMA Sunny Boy Bluetooth Home Assistant Integration currently supports:

* ☀️ Native SMA Bluetooth (RFCOMM) communication
* 🚫 No SBFspot required
* 🔍 Automatic inverter discovery
* 🏷️ Automatic model detection
* 🔢 Automatic serial number detection
* 🌙 Sleep mode handling
* 🔄 Automatic reconnect after sunrise
* ⚡ Real-time AC power monitoring
* 🌡️ Inverter temperature monitoring
* 📈 Daily energy production
* 📊 Lifetime energy production
* 📡 Bluetooth connection monitoring
* 📋 SMA Status sensor
* ⚙️ Home Assistant Config Flow
* 📦 HACS compatible

---

## ✅ Supported Models

### Confirmed working

| Manufacturer | Model               | Status   |
| ------------ | ------------------- | -------- |
| SMA          | Sunny Boy 4000TL-20 | ✅ Tested |

### Likely compatible

This integration is designed for older SMA inverters with Bluetooth support.

Potentially compatible devices:

* SMA Sunny Boy 1200
* SMA Sunny Boy 1700
* SMA Sunny Boy 2100
* SMA Sunny Boy 3000TL-20
* SMA Sunny Boy 3600TL-20
* SMA Sunny Boy 5000TL-20
* SMA Sunny Tripower Bluetooth models

If your inverter uses SMA Bluetooth RFCOMM communication, there is a good chance it will work.

Please open an issue if you successfully test another model.

---

## 📦 Installation

### HACS Installation

1. Open **HACS**
2. Go to **Integrations**
3. Open the menu in the top right corner
4. Select **Custom repositories**
5. Add this repository URL:

```text
https://github.com/shopsiamware/ha-sma-sunnyboy-bluetooth
```

6. Select category:

```text
Integration
```

7. Install **SMA Sunny Boy Bluetooth Home Assistant Integration**
8. Restart Home Assistant

---

### Manual Installation

Copy this folder:

```text
custom_components/sma_bt_native
```

to:

```text
config/custom_components/sma_bt_native
```

Restart Home Assistant afterwards.

---

## ⚙️ Configuration

After installation:

1. Open Home Assistant
2. Navigate to:

```text
Settings → Devices & Services → Add Integration
```

3. Search for:

```text
SMA Sunny Boy Bluetooth Home Assistant Integration
```

4. Enter the inverter Bluetooth MAC address
5. Enter your SMA user password
6. Complete setup

The integration will automatically detect:

* Inverter model
* Serial number
* Bluetooth address

---

## 🧩 Available Entities

### Sensors

* AC Power
* Energy Today
* Energy Total
* Inverter Temperature
* SMA Status

### Binary Sensors

* Bluetooth Connected

---

## 📋 SMA Status Sensor

The SMA Status sensor provides a simple operational state:

| State     | Description                         |
| --------- | ----------------------------------- |
| Producing | Inverter is generating power        |
| Sleeping  | Inverter is in night mode           |
| Offline   | Bluetooth communication unavailable |

---

## 🏡 Dashboard Example

Example values:

```text
Status: Producing
Power: 3482 W
Today: 18.6 kWh
Total: 42851 kWh
Temperature: 42.3 °C
Bluetooth: Connected
```

---

## 🛣️ Roadmap

Planned or possible future improvements:

* Bluetooth signal strength sensor
* Additional SMA model mappings
* Firmware version detection improvements
* Additional diagnostic entities
* More tested inverter models
* Improved translations

---

## 🤝 Contributing

Contributions are welcome.

You can help by:

* Testing additional SMA Bluetooth inverters
* Reporting bugs
* Sharing logs
* Improving translations
* Creating pull requests
* Suggesting new features

If you test another inverter model, please include:

* Exact inverter model
* Firmware version if available
* Working entities
* Non-working entities
* Relevant Home Assistant logs

---

## ⚠️ Disclaimer

This project is an independent community project.

This integration is not affiliated with, endorsed by, maintained by, or supported by SMA Solar Technology AG.

Use this integration at your own risk.

---

# Deutsch

## ✨ Funktionen

Die SMA Sunny Boy Bluetooth Home Assistant Integration unterstützt aktuell:

* ☀️ Native SMA Bluetooth-Kommunikation (RFCOMM)
* 🚫 Kein SBFspot erforderlich
* 🔍 Automatische Wechselrichter-Erkennung
* 🏷️ Automatische Modellerkennung
* 🔢 Automatische Seriennummer-Erkennung
* 🌙 Schlafmodus-Erkennung
* 🔄 Automatische Wiederverbindung nach Sonnenaufgang
* ⚡ AC-Leistung in Echtzeit
* 🌡️ Wechselrichtertemperatur
* 📈 Tagesertrag
* 📊 Gesamtertrag
* 📡 Bluetooth-Verbindungsüberwachung
* 📋 SMA Status Sensor
* ⚙️ Home Assistant Config Flow
* 📦 HACS-kompatibel

---

## ✅ Unterstützte Modelle

### Erfolgreich getestet

| Hersteller | Modell              | Status     |
| ---------- | ------------------- | ---------- |
| SMA        | Sunny Boy 4000TL-20 | ✅ Getestet |

### Wahrscheinlich kompatibel

Diese Integration wurde für ältere SMA-Wechselrichter mit Bluetooth-Unterstützung entwickelt.

Mögliche Kandidaten:

* SMA Sunny Boy 1200
* SMA Sunny Boy 1700
* SMA Sunny Boy 2100
* SMA Sunny Boy 3000TL-20
* SMA Sunny Boy 3600TL-20
* SMA Sunny Boy 5000TL-20
* SMA Sunny Tripower Bluetooth Modelle

Wenn dein Wechselrichter SMA Bluetooth RFCOMM verwendet, besteht eine gute Chance, dass er funktioniert.

Bitte erstelle ein Issue, wenn du ein weiteres Modell erfolgreich getestet hast.

---

## 📦 Installation

### Installation über HACS

1. **HACS** öffnen
2. Zu **Integrationen** wechseln
3. Menü oben rechts öffnen
4. **Benutzerdefinierte Repositories** auswählen
5. Folgende Repository-Adresse eintragen:

```text
https://github.com/shopsiamware/ha-sma-sunnyboy-bluetooth
```

6. Kategorie auswählen:

```text
Integration
```

7. **SMA Sunny Boy Bluetooth Home Assistant Integration** installieren
8. Home Assistant neu starten

---

### Manuelle Installation

Diesen Ordner:

```text
custom_components/sma_bt_native
```

nach:

```text
config/custom_components/sma_bt_native
```

kopieren.

Anschließend Home Assistant neu starten.

---

## ⚙️ Einrichtung

Nach der Installation:

1. Home Assistant öffnen
2. Zu folgendem Menü wechseln:

```text
Einstellungen → Geräte & Dienste → Integration hinzufügen
```

3. Nach folgender Integration suchen:

```text
SMA Sunny Boy Bluetooth Home Assistant Integration
```

4. Bluetooth-MAC-Adresse des Wechselrichters eingeben
5. SMA-Benutzerpasswort eingeben
6. Einrichtung abschließen

Die Integration erkennt automatisch:

* Wechselrichter-Modell
* Seriennummer
* Bluetooth-Adresse

---

## 🧩 Verfügbare Entitäten

### Sensoren

* AC-Leistung
* Tagesertrag
* Gesamtertrag
* Wechselrichtertemperatur
* SMA Status

### Binärsensoren

* Bluetooth verbunden

---

## 📋 SMA Status Sensor

Der SMA Status Sensor liefert den aktuellen Betriebszustand:

| Status    | Beschreibung                               |
| --------- | ------------------------------------------ |
| Producing | Wechselrichter produziert Energie          |
| Sleeping  | Wechselrichter befindet sich im Nachtmodus |
| Offline   | Bluetooth-Kommunikation nicht verfügbar    |

---

## 🏡 Dashboard-Beispiel

```text
Status: Producing
Leistung: 3482 W
Heute: 18,6 kWh
Gesamt: 42851 kWh
Temperatur: 42,3 °C
Bluetooth: Verbunden
```

---

## 🛣️ Roadmap

Geplante oder mögliche Erweiterungen:

* Bluetooth-Signalstärke
* Weitere SMA-Modell-Erkennung
* Verbesserte Firmware-Erkennung
* Zusätzliche Diagnose-Entitäten
* Weitere getestete Wechselrichter
* Verbesserte Übersetzungen

---

## 🤝 Mitwirken

Beiträge sind willkommen.

Du kannst helfen durch:

* Tests weiterer SMA Bluetooth-Wechselrichter
* Fehlermeldungen
* Bereitstellung von Logs
* Verbesserung von Übersetzungen
* Pull Requests
* Feature-Wünsche

Wenn du ein weiteres Modell testest, gib bitte möglichst an:

* Exaktes Wechselrichter-Modell
* Firmware-Version (falls verfügbar)
* Funktionierende Entitäten
* Nicht funktionierende Entitäten
* Relevante Home-Assistant-Logs

---

## ⚠️ Haftungsausschluss

Dieses Projekt ist ein unabhängiges Community-Projekt.

Diese Integration steht in keiner Verbindung zu SMA Solar Technology AG und wird weder von SMA unterstützt noch gepflegt oder empfohlen.

Die Nutzung erfolgt auf eigene Verantwortung.
