# ☀️🔵 SMA Sunny Boy Bluetooth Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz/)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Custom%20Integration-41BDF5.svg)](https://www.home-assistant.io/)
[![GitHub release](https://img.shields.io/github/v/release/MTTPoll/ha-sma-sunnyboy-bluetooth?display_name=tag)](https://github.com/MTTPoll/ha-sma-sunnyboy-bluetooth/releases)
[![GitHub issues](https://img.shields.io/github/issues/MTTPoll/ha-sma-sunnyboy-bluetooth)](https://github.com/MTTPoll/ha-sma-sunnyboy-bluetooth/issues)

**SMA Sunny Boy Bluetooth Home Assistant Integration** is a Home Assistant custom integration for legacy **SMA Sunny Boy** and **SMA Sunny Tripower** inverters using native Bluetooth communication.

It connects directly to your inverter using SMA Bluetooth RFCOMM communication and does **not require SBFspot**, Sunny Explorer or any external software.

> Currently tested with the **SMA Sunny Boy 4000TL-20** running firmware **03.01.03.04**.
>
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
* 🏷️ Automatic firmware version detection
* ⏱️ Inverter operation time
* 🔌 Inverter feed-in time
* 🌙 Sleep mode handling
* 🔄 Automatic reconnect after sunrise
* ⚡ Real-time AC power monitoring
* ⚡ MPPT1 Power monitoring
* ⚡ MPPT2 Power monitoring
* ⚡ DC Total Power monitoring
* 📈 Inverter Efficiency monitoring
* 🌡️ Inverter temperature monitoring
* 📈 Daily energy production
* 📊 Lifetime energy production
* 📶 Bluetooth signal strength monitoring
* 📡 Bluetooth connection monitoring
* 📋 SMA Status sensor
* ⚙️ Home Assistant Config Flow
* 📦 HACS compatible

---

## ✅ Supported Models

### Confirmed working

| Manufacturer | Model               | Firmware    | Status |
| ------------ | ------------------- | ----------- | ------ |
| SMA          | Sunny Boy 4000TL-20 | 03.01.03.04 | ✅ Tested |

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

## ℹ️ Startup Behavior

To prevent Home Assistant startup delays, the integration intentionally waits until Home Assistant has fully completed its startup sequence.

The first inverter connection attempt is started approximately 30 seconds after Home Assistant reports that startup is complete.

As a result:

- Sensors may initially appear as unavailable after a Home Assistant restart.
- Values are typically available within 30–60 seconds.
- This behavior is intentional and prevents Bluetooth connection attempts from delaying other Home Assistant integrations during startup.

If your inverter is sleeping (for example during nighttime), the integration will automatically retry later and reconnect when the inverter becomes available again.

---

## 📦 Installation

### HACS Installation

1. Open **HACS**
2. Go to **Integrations**
3. Open the menu in the top right corner
4. Select **Custom repositories**
5. Add this repository URL:

```text
https://github.com/MTTPoll/ha-sma-sunnyboy-bluetooth
```

6. Select category:

```text
Integration
```

7. Install **SMA Sunny Boy Bluetooth Home Assistant Integration**
8. Restart Home Assistant

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
* Firmware version
* Bluetooth address

---

## 🧩 Available Entities

### Sensors

* AC Power
* Energy Today
* Energy Total
* Inverter Temperature
* Operation Time
* Feed-In Time
* MPPT1 Power
* MPPT2 Power
* DC Total Power
* Efficiency
* Bluetooth Signal Strength
* SMA Status

### Binary Sensors

* Bluetooth Connected

---

## 📋 SMA Status Sensor

| State     | Description                         |
| --------- | ----------------------------------- |
| Producing | Inverter is generating power        |
| Sleeping  | Inverter is in night mode           |
| Offline   | Bluetooth communication unavailable |

---

## 🏡 Dashboard Example

```text
Status: Producing

AC Power: 951 W

MPPT1 Power: 625 W
MPPT2 Power: 337 W
DC Total Power: 962 W

Efficiency: 98.86 %

Energy Today: 18.6 kWh
Energy Total: 42851 kWh

Temperature: 42.3 °C

Operation Time: 68182 h
Feed-In Time: 66427 h

Bluetooth Signal: 73.7 %

Firmware: 03.01.03.04

Bluetooth: Connected
```

---

## 🛣️ Roadmap

Planned or possible future improvements:

* Grid Frequency sensor
* Grid Relay Status
* Additional SMA model mappings
* Additional diagnostic entities
* More tested inverter models
* Improved translations
* Additional firmware compatibility testing

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
* 🏷️ Automatische Firmware-Erkennung
* ⏱️ Betriebszeit des Wechselrichters
* 🔌 Einspeisezeit des Wechselrichters
* 🌙 Schlafmodus-Erkennung
* 🔄 Automatische Wiederverbindung nach Sonnenaufgang
* ⚡ AC-Leistung in Echtzeit
* ⚡ MPPT1-Leistung
* ⚡ MPPT2-Leistung
* ⚡ DC-Gesamtleistung
* 📈 Wirkungsgrad
* 🌡️ Wechselrichtertemperatur
* 📈 Tagesertrag
* 📊 Gesamtertrag
* 📶 Bluetooth-Signalstärke
* 📡 Bluetooth-Verbindungsüberwachung
* 📋 SMA Status Sensor
* ⚙️ Home Assistant Config Flow
* 📦 HACS-kompatibel

---

## ✅ Unterstützte Modelle

### Erfolgreich getestet

| Hersteller | Modell | Firmware | Status |
|------------|---------|----------|---------|
| SMA | Sunny Boy 4000TL-20 | 03.01.03.04 | ✅ Getestet |

---

## ℹ️ Startverhalten

Um den Start von Home Assistant nicht zu verzögern, wartet die Integration bewusst darauf, dass Home Assistant vollständig gestartet ist.

Der erste Verbindungsversuch zum Wechselrichter erfolgt ungefähr 30 Sekunden nach Abschluss des Home-Assistant-Starts.

Dadurch kann es nach einem Neustart vorkommen, dass:

- Sensoren zunächst als „Nicht verfügbar“ angezeigt werden.
- Die ersten Werte erst nach etwa 30–60 Sekunden erscheinen.
- Dieses Verhalten ist beabsichtigt und verhindert, dass Bluetooth-Verbindungen andere Integrationen beim Start blockieren.

Befindet sich der Wechselrichter im Nachtmodus, versucht die Integration später automatisch erneut eine Verbindung aufzubauen und verbindet sich nach dem Aufwachen des Wechselrichters selbstständig.

---

## 📦 Installation

### Installation über HACS

1. HACS öffnen
2. Zu Integrationen wechseln
3. Benutzerdefinierte Repositories auswählen
4. Repository hinzufügen:

```text
https://github.com/MTTPoll/ha-sma-sunnyboy-bluetooth
```

5. Kategorie auswählen:

```text
Integration
```

6. Integration installieren
7. Home Assistant neu starten

---

## ⚙️ Einrichtung

1. Einstellungen → Geräte & Dienste
2. Integration hinzufügen
3. SMA Sunny Boy Bluetooth Home Assistant Integration auswählen
4. Bluetooth-MAC-Adresse eingeben
5. SMA-Passwort eingeben
6. Einrichtung abschließen

---

## 🧩 Verfügbare Entitäten

### Sensoren

* AC-Leistung
* Tagesertrag
* Gesamtertrag
* Wechselrichtertemperatur
* Betriebszeit
* Einspeisezeit
* MPPT1-Leistung
* MPPT2-Leistung
* DC-Gesamtleistung
* Wirkungsgrad
* Bluetooth-Signalstärke
* SMA Status

### Binärsensoren

* Bluetooth verbunden

---

## 📋 SMA Status Sensor

| Status | Beschreibung |
|---------|-------------|
| Producing | Wechselrichter produziert Energie |
| Sleeping | Nachtmodus |
| Offline | Keine Bluetooth-Verbindung |

---

## 🏡 Dashboard-Beispiel

```text
Status: Producing

AC-Leistung: 951 W

MPPT1-Leistung: 625 W
MPPT2-Leistung: 337 W
DC-Gesamtleistung: 962 W

Wirkungsgrad: 98.86 %

Tagesertrag: 18,6 kWh
Gesamtertrag: 42851 kWh

Temperatur: 42,3 °C

Betriebszeit: 68182 h
Einspeisezeit: 66427 h

Bluetooth-Signal: 73.7 %

Firmware: 03.01.03.04

Bluetooth: Verbunden
```

---

## 🛣️ Roadmap

Geplante Erweiterungen:

* Netzfrequenz-Sensor
* Netzrelais-Status
* Weitere SMA-Modell-Erkennung
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

---

## ⚠️ Haftungsausschluss

Dieses Projekt ist ein unabhängiges Community-Projekt.

Diese Integration steht in keiner Verbindung zu SMA Solar Technology AG und wird weder von SMA unterstützt noch gepflegt oder empfohlen.

Die Nutzung erfolgt auf eigene Verantwortung.
