# SMA Sunny Boy Bluetooth Home Assistant Integration

A native Home Assistant custom integration for older SMA Sunny Boy and Sunny Tripower inverters with classic Bluetooth / RFCOMM support.

This integration talks directly to the inverter over Bluetooth. It does **not** require SBFspot, MQTT, Modbus, Speedwire, or an external database.

> This project is intended for legacy SMA Bluetooth inverters. It is not affiliated with, endorsed by, or supported by SMA Solar Technology AG.

## Features

- Native SMA Bluetooth RFCOMM communication
- Home Assistant Config Flow setup
- Manual Bluetooth MAC address setup
- Stable deferred startup after Home Assistant has fully started
- Persistent Bluetooth session with reconnect handling
- Night / sleep mode backoff to avoid constant reconnect attempts
- Automatic serial number detection from Bluetooth device information
- Automatic inverter model detection through the SMA protocol
- Home Assistant device registry support
- HACS compatible repository structure

## Entities

### Sensors

| Entity | Unit | Description |
| --- | --- | --- |
| AC Power | W | Current inverter AC output power |
| Energy Today | kWh | Daily energy production |
| Energy Total | kWh | Lifetime energy production |
| Inverter Temperature | °C | Internal inverter temperature, if supported by the inverter |

### Binary sensors

| Entity | Description |
| --- | --- |
| Bluetooth Connected | Shows whether the last successful SMA communication was recent |

## Device information

The integration exposes Home Assistant device information where available:

- Manufacturer: SMA
- Model, for example `SB 4000TL-20`
- Serial number
- Bluetooth address
- Firmware version, when supported and decoded

## Tested device

Tested with:

- SMA Sunny Boy 4000TL-20

## Likely compatible devices

This integration should work with many older SMA inverters that support classic Bluetooth RFCOMM communication, especially devices from the Sunny Boy Bluetooth generation.

Likely compatible examples:

- SMA Sunny Boy 1200 / 1700 / 2100
- SMA Sunny Boy 3000TL-20
- SMA Sunny Boy 3600TL-20
- SMA Sunny Boy 4000TL-20
- SMA Sunny Boy 5000TL-20
- Older Sunny Tripower Bluetooth models

Compatibility may vary by firmware and model. Unknown model codes can be added to the internal device type table when users report them.

## Not supported

This integration does not support:

- Speedwire-only devices
- WebConnect-only devices
- ennexOS devices
- Modern SMA devices without classic Bluetooth RFCOMM
- Bluetooth Low Energy-only devices

## Requirements

- Home Assistant OS or Home Assistant Supervised/Core on Linux
- Bluetooth adapter available to Home Assistant
- SMA inverter with classic Bluetooth enabled
- Bluetooth address of the inverter, for example `00:80:25:16:38:CC`
- SMA user password

## Installation with HACS

1. Open HACS.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL.
5. Select category **Integration**.
6. Install **SMA Sunny Boy Bluetooth Home Assistant Integration**.
7. Restart Home Assistant.
8. Add the integration via **Settings → Devices & services → Add integration**.

## Manual installation

Copy this folder:

```text
custom_components/sma_bt_native
```

into your Home Assistant configuration directory:

```text
/config/custom_components/sma_bt_native
```

Restart Home Assistant and add the integration from the UI.

## Configuration

During setup, enter:

- Bluetooth address
- SMA user password
- Optional polling intervals

Default polling intervals:

| Value | Default |
| --- | ---: |
| AC Power | 30 seconds |
| Energy Today | 180 seconds |
| Energy Total | 180 seconds |
| Inverter Temperature | 60 seconds |

## Notes about night mode

Older SMA Bluetooth inverters may stop responding at night when the inverter goes to sleep. This is expected behavior.

The integration treats this as a normal sleep state and backs off reconnect attempts instead of flooding the Bluetooth stack or filling the Home Assistant log with errors.

## Troubleshooting

### No values after restart

The integration intentionally waits until Home Assistant has fully started before opening the Bluetooth connection. Values can appear shortly after startup instead of immediately.

### Device is unavailable at night

This is usually normal. The inverter may be asleep. Values should return automatically after sunrise when the inverter wakes up.

### Model is unknown

The integration reads the model code from the SMA nameplate registers. If your inverter works but the model is unknown, open an issue and include the debug log lines for `SMA device type code`.

To enable debug logging:

```yaml
logger:
  logs:
    custom_components.sma_bt_native: debug
```

## Credits

This integration was developed and tested with an SMA Sunny Boy 4000TL-20 on Home Assistant OS using native Python RFCOMM communication.

The project was inspired by the long-standing SMA Bluetooth protocol work in the community, including SBFspot. SBFspot is not required to use this integration.

---

# Deutsch

Eine native Home Assistant Custom Integration für ältere SMA Sunny Boy und Sunny Tripower Wechselrichter mit klassischem Bluetooth / RFCOMM.

Die Integration kommuniziert direkt per Bluetooth mit dem Wechselrichter. Es wird **kein** SBFspot, MQTT, Modbus, Speedwire oder eine externe Datenbank benötigt.

> Dieses Projekt ist für ältere SMA Bluetooth Wechselrichter gedacht. Es ist nicht mit SMA Solar Technology AG verbunden und wird nicht von SMA unterstützt.

## Funktionen

- Native SMA Bluetooth RFCOMM Kommunikation
- Einrichtung über Home Assistant Config Flow
- Manuelle Eingabe der Bluetooth-MAC-Adresse
- Verzögerter Start nach abgeschlossenem Home-Assistant-Start
- Persistente Bluetooth-Session mit Reconnect-Handling
- Nacht-/Schlafmodus-Erkennung mit Backoff
- Automatische Seriennummer-Erkennung aus Bluetooth-Daten
- Automatische Modellerkennung über das SMA-Protokoll
- Home Assistant Device Registry Support
- HACS-kompatible Repository-Struktur

## Entitäten

### Sensoren

| Entität | Einheit | Beschreibung |
| --- | --- | --- |
| AC Power | W | Aktuelle AC-Ausgangsleistung des Wechselrichters |
| Energy Today | kWh | Tagesertrag |
| Energy Total | kWh | Gesamtertrag / Lifetime-Ertrag |
| Inverter Temperature | °C | Interne Wechselrichtertemperatur, falls vom Gerät unterstützt |

### Binärsensoren

| Entität | Beschreibung |
| --- | --- |
| Bluetooth Connected | Zeigt an, ob die letzte erfolgreiche SMA-Kommunikation kürzlich erfolgt ist |

## Geräteinformationen

Die Integration stellt, soweit verfügbar, Geräteinformationen in Home Assistant bereit:

- Hersteller: SMA
- Modell, zum Beispiel `SB 4000TL-20`
- Seriennummer
- Bluetooth-Adresse
- Firmware-Version, sofern unterstützt und dekodiert

## Getestetes Gerät

Getestet mit:

- SMA Sunny Boy 4000TL-20

## Wahrscheinlich kompatible Geräte

Die Integration sollte mit vielen älteren SMA-Wechselrichtern funktionieren, die klassisches Bluetooth RFCOMM unterstützen, insbesondere Geräte der Sunny-Boy-Bluetooth-Generation.

Wahrscheinlich kompatible Beispiele:

- SMA Sunny Boy 1200 / 1700 / 2100
- SMA Sunny Boy 3000TL-20
- SMA Sunny Boy 3600TL-20
- SMA Sunny Boy 4000TL-20
- SMA Sunny Boy 5000TL-20
- ältere Sunny Tripower Bluetooth Modelle

Die Kompatibilität kann je nach Firmware und Modell abweichen. Unbekannte Modellcodes können ergänzt werden, wenn Nutzer sie melden.

## Nicht unterstützt

Nicht unterstützt werden:

- reine Speedwire-Geräte
- reine WebConnect-Geräte
- ennexOS-Geräte
- moderne SMA-Geräte ohne klassisches Bluetooth RFCOMM
- reine Bluetooth-Low-Energy-Geräte

## Voraussetzungen

- Home Assistant OS oder Home Assistant Supervised/Core unter Linux
- Bluetooth-Adapter für Home Assistant verfügbar
- SMA-Wechselrichter mit aktiviertem klassischem Bluetooth
- Bluetooth-Adresse des Wechselrichters, zum Beispiel `00:80:25:16:38:CC`
- SMA Benutzer-Passwort

## Installation mit HACS

1. HACS öffnen.
2. Zu **Integrationen** wechseln.
3. Über das Drei-Punkte-Menü **Benutzerdefinierte Repositories** öffnen.
4. Diese Repository-URL hinzufügen.
5. Kategorie **Integration** wählen.
6. **SMA Sunny Boy Bluetooth Home Assistant Integration** installieren.
7. Home Assistant neu starten.
8. Integration über **Einstellungen → Geräte & Dienste → Integration hinzufügen** einrichten.

## Manuelle Installation

Diesen Ordner kopieren:

```text
custom_components/sma_bt_native
```

nach:

```text
/config/custom_components/sma_bt_native
```

Danach Home Assistant neu starten und die Integration über die Benutzeroberfläche hinzufügen.

## Konfiguration

Bei der Einrichtung werden eingetragen:

- Bluetooth-Adresse
- SMA Benutzer-Passwort
- optionale Abfrageintervalle

Standardintervalle:

| Wert | Standard |
| --- | ---: |
| AC-Leistung | 30 Sekunden |
| Tagesenergie | 180 Sekunden |
| Gesamtenergie | 180 Sekunden |
| Wechselrichtertemperatur | 60 Sekunden |

## Hinweise zum Nachtbetrieb

Ältere SMA Bluetooth Wechselrichter reagieren nachts eventuell nicht, weil der Wechselrichter schläft. Das ist normales Verhalten.

Die Integration behandelt diesen Zustand als erwarteten Schlafmodus und reduziert erneute Verbindungsversuche, statt den Bluetooth-Stack oder das Home-Assistant-Log unnötig zu belasten.

## Fehlersuche

### Nach Neustart erscheinen nicht sofort Werte

Die Integration wartet bewusst, bis Home Assistant vollständig gestartet ist, bevor die Bluetooth-Verbindung geöffnet wird. Die Werte erscheinen daher kurz nach dem Start.

### Gerät ist nachts nicht verfügbar

Das ist meist normal. Der Wechselrichter schläft. Nach Sonnenaufgang sollten die Werte automatisch zurückkommen.

### Modell wird nicht erkannt

Die Integration liest den Modellcode aus den SMA-Nameplate-Registern. Wenn dein Wechselrichter funktioniert, aber das Modell unbekannt ist, erstelle ein Issue und füge die Debug-Logzeilen zu `SMA device type code` hinzu.

Debug-Logging aktivieren:

```yaml
logger:
  logs:
    custom_components.sma_bt_native: debug
```

## Credits

Diese Integration wurde mit einem SMA Sunny Boy 4000TL-20 auf Home Assistant OS entwickelt und getestet. Die Kommunikation erfolgt nativ über Python RFCOMM.

Das Projekt wurde von der langjährigen Arbeit der Community am SMA-Bluetooth-Protokoll inspiriert, unter anderem SBFspot. SBFspot wird für diese Integration nicht benötigt.
