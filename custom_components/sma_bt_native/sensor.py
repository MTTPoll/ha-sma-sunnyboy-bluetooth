from __future__ import annotations

import logging
import socket
from dataclasses import dataclass

from .const import (
    SENSOR_AC_POWER,
    SENSOR_ENERGY_TODAY,
    SENSOR_ENERGY_TOTAL,
    SENSOR_TEMPERATURE,
    SENSOR_OPERATION_TIME,
    SENSOR_FEED_IN_TIME,
)

_LOGGER = logging.getLogger(__name__)


class SMAError(Exception):
    pass


def b16(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF])


def b32(v):
    return bytes([v & 0xFF, (v >> 8) & 0xFF, (v >> 16) & 0xFF, (v >> 24) & 0xFF])


def u16(b):
    return b[0] | (b[1] << 8)


def u32(b):
    return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)


def u64(b):
    return u32(b[0:4]) | (u32(b[4:8]) << 32)


def mac_bytes(mac):
    return bytes(int(x, 16) for x in mac.split(":"))[::-1]


def crc16(data):
    crc = 0xFFFF
    for c in data:
        crc ^= c
        for _ in range(8):
            crc = (crc >> 1) ^ 0x8408 if crc & 1 else crc >> 1
    return (~crc) & 0xFFFF


def make_ppp(payload):
    frame = bytearray(b"\xff\x03") + b16(0x6560) + bytearray(payload)
    frame += b16(crc16(frame))

    raw = bytearray([0x7E])
    for x in frame:
        if x in (0x7E, 0x7D, 0x11, 0x13):
            raw += bytes([0x7D, x ^ 0x20])
        else:
            raw.append(x)
    raw.append(0x7E)
    return raw


def unescape_ppp(raw):
    if not raw or raw[0] != 0x7E:
        raise SMAError("Invalid PPP frame")

    raw = bytearray(raw[1:-1])
    out = bytearray()
    i = 0

    while i < len(raw):
        if raw[i] == 0x7D:
            out.append(raw[i + 1] ^ 0x20)
            i += 2
        else:
            out.append(raw[i])
            i += 1

    return out


@dataclass
class SMAResponse:
    error: int
    pktcount: int
    tag: int
    typ: int
    response: bool
    subtype: int
    arg1: int
    arg2: int
    extra: bytearray


@dataclass
class SMADeviceInfo:
    model: str | None = None
    model_code: int | None = None
    device_class: str | None = None
    class_code: int | None = None
    sw_version: str | None = None


DEVICE_TYPES = {
    # SMA/SBFspot direct codes.
    9066: "SB 1200",
    9160: "SB 3600TL-20",
    9161: "SB 4000TL-20",
    9162: "SB 5000TL-20",
    9281: "STP 10000TL-20",
    9282: "STP 11000TL-20",
    9283: "STP 12000TL-20",

    # Observed NameplateModel tag values on SB 4000TL-20:
    # raw payload: 66 01 00 01 67 01 00 00 ...
    # little-endian u16 values include 0x0166 and 0x0167.
    358: "SB 4000TL-20",
    359: "SB 4000TL-20",
}

DEVICE_CLASSES = {
    8000: "All Devices",
    8001: "Solar Inverters",
    8002: "Wind Turbine Inverter",
    8007: "Battery Inverters",
    8033: "Consumer",
    8064: "Sensor System",
    8065: "Electricity Meter",
    8128: "Communication Products",
}


def _decode_sw_version(raw: int) -> str | None:
    if raw in (
        0,
        0xFFFFFFFF,
        0xFFFFFFFE,
        0xFFFFFEFE,
        0xFEFFFFFE,
    ):
        return None

    b = raw.to_bytes(4, "big")
    return f"{b[0]:02d}.{b[1]:02d}.{b[2]:02d}.{b[3]:02d}"


def _first_valid_numeric(values: list[int]) -> int | None:
    for value in values:
        if value not in (0, 0xFFFFFFFF, 0xFFFFFEFE, 0xFEFFFFFE):
            return value
    return None


def _u16_values(payload: bytes) -> list[int]:
    return [
        u16(payload[i : i + 2])
        for i in range(0, min(len(payload), 32), 2)
        if len(payload[i : i + 2]) == 2
    ]


def _first_valid_u16(values: list[int]) -> int | None:
    for value in values:
        if value not in (0, 0xFFFF, 0xFFFE, 0x00FF):
            return value
    return None


def is_valid_sma_value(value: int | None) -> bool:
    """Return False for SMA invalid/not-available marker values.

    Some SMA Bluetooth inverters still answer while going to sleep, but return
    marker values such as 0x80000000 instead of real measurements. These must
    not be published as Home Assistant sensor values.
    """
    return value not in (
        None,
        0x80000000,
        0xFFFFFFFF,
        0xFFFFFEFE,
        0xFEFFFFFE,
    )


class SMABluetoothClient:
    def __init__(self, bt_address, password, timeout=8):
        self.bt_address = bt_address
        self.password = password
        self.timeout = timeout
        self.sock = None
        self.tag = 0
        self._logged_in = False

    def _next_tag(self):
        self.tag += 1
        return self.tag

    def _connect(self):
        if self.sock:
            return

        self.sock = socket.socket(
            socket.AF_BLUETOOTH,
            socket.SOCK_STREAM,
            socket.BTPROTO_RFCOMM,
        )
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.bt_address, 1))

    def _close(self):
        if self.sock:
            try:
                self.sock.close()
            finally:
                self.sock = None
                self._logged_in = False

    def close(self):
        self._close()

    def _ensure_session(self):
        if self.sock and self._logged_in:
            return

        self._close()
        self._connect()
        self._hello()
        self._login()
        self._logged_in = True

    def _recv(self, size=4096):
        if not self.sock:
            raise SMAError("Socket not connected")
        return bytearray(self.sock.recv(size))

    def _send_outer(self, src, dst, typ, payload):
        if not self.sock:
            raise SMAError("Socket not connected")

        pktlen = len(payload) + 18
        pkt = bytearray([0x7E, pktlen, 0x00, pktlen ^ 0x7E])
        pkt += mac_bytes(src) + mac_bytes(dst) + b16(typ) + bytearray(payload)
        self.sock.send(bytes(pkt))

    def _decode_6560(self, pkt):
        ppp = unescape_ppp(bytearray(pkt[18:]))
        data = ppp[4:-2]

        tag_raw = u16(data[22:24])
        typ_raw = u16(data[24:26])

        return SMAResponse(
            u16(data[18:20]),
            u16(data[20:22]),
            tag_raw & 0x7FFF,
            typ_raw & ~1,
            bool(typ_raw & 1),
            u16(data[26:28]),
            u32(data[28:32]),
            u32(data[32:36]),
            data[36:],
        )

    def _send_6560(
        self,
        tag,
        typ,
        subtype,
        arg1,
        arg2,
        extra=b"",
        b1=0,
        b2=0,
        c1=0,
        c2=0,
    ):
        inner = bytearray()
        inner.append((len(extra) + 36) // 4)
        inner.append(0xA0)

        inner += (
            b"\xff\xff\xff\xff\xff\xff"
            + bytes([b1, b2])
            + b"\x00\x00\x00\x00\x00\x00"
            + bytes([c1, c2])
            + b"\x00\x00\x00\x00"
        )
        inner += (
            b16(tag | 0x8000)
            + b16(typ)
            + b16(subtype)
            + b32(arg1)
            + b32(arg2)
            + bytearray(extra)
        )

        self._send_outer(
            "00:00:00:00:00:00",
            "ff:ff:ff:ff:ff:ff",
            0x01,
            make_ppp(inner),
        )

    def _hello(self):
        hello = self._recv(512)
        self._send_outer("00:00:00:00:00:00", self.bt_address, 0x02, hello[18:])

        for _ in range(3):
            self._recv(1024)

    def _login(self):
        pw = self.password.encode("ascii")
        pw += b"\x00" * (12 - len(pw))
        pw = bytes(((c + 0x88) % 0xFF) for c in pw)

        extra = b"\xaa\xaa\xbb\xbb" + b"\x00\x00\x00\x00" + pw
        tag = self._next_tag()

        self._send_6560(
            tag,
            0x040C,
            0xFFFD,
            7,
            900,
            extra,
            b1=0,
            b2=1,
            c1=0,
            c2=1,
        )

        resp = self._decode_6560(self._recv(2048))
        if resp.error:
            raise SMAError(f"Login failed with SMA error 0x{resp.error:x}")

    def _request_raw_extra(self, subtype, first, last):
        tag = self._next_tag()
        self._send_6560(tag, 0x0200, subtype, first, last)

        resp = self._decode_6560(self._recv(4096))
        if resp.error:
            raise SMAError(
                f"Request {first:08x}-{last:08x} failed with SMA error 0x{resp.error:x}"
            )

        return resp.extra

    def _request(self, subtype, first, last):
        extra = self._request_raw_extra(subtype, first, last)
        return parse_records(extra)

    def _request_nameplate_record(self, lri: int) -> tuple[int, int, list[int], list[int], bytes] | None:
        """Read one SMA nameplate LRI as a single 40-byte record.

        SBFspot reads NameplateLocation, NameplateMainModel and NameplateModel
        as individual 40-byte records. Requesting the full 0x00821E00-0x008220FF
        range can return variable/truncated records on some Bluetooth inverters.
        """

        extra = self._request_raw_extra(0x5800, lri, lri | 0xFF)
        _LOGGER.debug("SMA nameplate LRI %08x raw extra: %s", lri, extra.hex())

        if len(extra) < 8:
            return None

        rec_lri = u32(extra[0:4])
        timestamp = u32(extra[4:8])
        payload = bytes(extra[8:])

        values32 = [
            u32(payload[i : i + 4])
            for i in range(0, min(len(payload), 32), 4)
            if len(payload[i : i + 4]) == 4
        ]
        values16 = _u16_values(payload)

        _LOGGER.debug(
            "SMA nameplate LRI %08x decoded rec_lri=%08x ts=%s u32=%s u16=%s ascii=%r",
            lri,
            rec_lri,
            timestamp,
            values32,
            values16,
            payload.rstrip(b"\x00"),
        )

        return rec_lri, timestamp, values32, values16, payload

    def read_device_info(self) -> SMADeviceInfo:
        """Read inverter type label and software version via SMA protocol."""

        self._ensure_session()
        info = SMADeviceInfo()

        try:
            # 0x00821E00: NameplateLocation / device name.
            self._request_nameplate_record(0x00821E00)
        except Exception as err:
            _LOGGER.debug("Could not read SMA NameplateLocation: %s", err)
            self._close()

        try:
            # 0x00821F00: NameplateMainModel / device class.
            record = self._request_nameplate_record(0x00821F00)
            if record:
                _rec_lri, _ts, values32, values16, _payload = record
                value = _first_valid_u16(values16) or _first_valid_numeric(values32)
                if value is not None:
                    info.class_code = value
                    info.device_class = DEVICE_CLASSES.get(value)
                    _LOGGER.debug(
                        "SMA device class code=%s label=%s",
                        value,
                        info.device_class,
                    )
        except Exception as err:
            _LOGGER.debug("Could not read SMA NameplateMainModel: %s", err)
            self._close()

        try:
            # 0x00822000: NameplateModel / device type.
            record = self._request_nameplate_record(0x00822000)
            if record:
                _rec_lri, _ts, values32, values16, _payload = record

                # NameplateModel on this Bluetooth generation is encoded as
                # 16-bit tag values, not as the first 32-bit integer.
                candidate_values = values16 + values32
                for value in candidate_values:
                    if value in DEVICE_TYPES:
                        info.model_code = value
                        info.model = DEVICE_TYPES[value]
                        break

                if info.model is None:
                    value = _first_valid_u16(values16) or _first_valid_numeric(values32)
                    if value is not None:
                        info.model_code = value

                _LOGGER.debug(
                    "SMA device type code=%s label=%s candidates_u16=%s candidates_u32=%s",
                    info.model_code,
                    info.model,
                    values16,
                    values32,
                )
        except Exception as err:
            _LOGGER.debug("Could not read SMA NameplateModel: %s", err)
            self._close()

        try:
            records = self._request(0x5800, 0x00823400, 0x008234FF)
            _LOGGER.debug("SMA Software raw records: %s", records)

            for _code, _lri, _cls, _ts, vals in records:
                for value in vals:
                    version = _decode_sw_version(value)
                    if version:
                        info.sw_version = version
                        break

                if info.sw_version:
                    break

        except Exception as err:
            _LOGGER.debug("Could not read SMA software version: %s", err)
            self._close()

        return info

    def read_values(self, sensors=None):
        wanted = set(
            sensors
            or (
                SENSOR_AC_POWER,
                SENSOR_ENERGY_TODAY,
                SENSOR_ENERGY_TOTAL,
                SENSOR_TEMPERATURE,
                SENSOR_OPERATION_TIME,
                SENSOR_FEED_IN_TIME,
            )
        )

        try:
            self._ensure_session()
            values = {sensor: None for sensor in wanted}

            if SENSOR_ENERGY_TOTAL in wanted or SENSOR_ENERGY_TODAY in wanted:
                for code, lri, cls, ts, vals in self._request(
                    0x5400,
                    0x00260100,
                    0x002622FF,
                ):
                    if lri == 0x00260100 and vals and SENSOR_ENERGY_TOTAL in wanted:
                        raw = vals[0]
                        if is_valid_sma_value(raw):
                            values[SENSOR_ENERGY_TOTAL] = round(raw / 1000, 3)
                    elif lri == 0x00262200 and vals and SENSOR_ENERGY_TODAY in wanted:
                        raw = vals[0]
                        if is_valid_sma_value(raw):
                            values[SENSOR_ENERGY_TODAY] = round(raw / 1000, 3)

            if (
                SENSOR_OPERATION_TIME in wanted
                or SENSOR_FEED_IN_TIME in wanted
            ):
                for code, lri, cls, ts, vals in self._request(
                    0x5400,
                    0x00462E00,
                    0x00462FFF,
                ):
                    if not vals:
                        continue

                    raw = vals[0]

                    if not is_valid_sma_value(raw):
                        continue

                    if lri == 0x00462E00 and SENSOR_OPERATION_TIME in wanted:
                        values[SENSOR_OPERATION_TIME] = round(raw / 3600, 2)

                    elif lri == 0x00462F00 and SENSOR_FEED_IN_TIME in wanted:
                        values[SENSOR_FEED_IN_TIME] = round(raw / 3600, 2)

            if SENSOR_AC_POWER in wanted:
                for code, lri, cls, ts, vals in self._request(
                    0x5100,
                    0x00263F00,
                    0x00263FFF,
                ):
                    if lri == 0x00263F00 and vals:
                        raw = vals[2] if len(vals) >= 3 else vals[0]
                        if is_valid_sma_value(raw):
                            values[SENSOR_AC_POWER] = int(raw)

            if SENSOR_TEMPERATURE in wanted:
                try:
                    for code, lri, cls, ts, vals in self._request(
                        0x5200,
                        0x00237700,
                        0x002377FF,
                    ):
                        if lri == 0x00237700 and vals:
                            raw = vals[2] if len(vals) >= 3 else vals[0]
                            if is_valid_sma_value(raw):
                                values[SENSOR_TEMPERATURE] = round(raw / 100, 2)
                except SMAError:
                    pass

            return values

        except Exception:
            self._close()
            raise

    def read_minimal_values(self):
        return self.read_values()


def parse_records(extra):
    extra = bytearray(extra)
    if not extra:
        return []

    for size in (16, 28, 40):
        if len(extra) >= size and len(extra) % size == 0:
            records = []

            for i in range(0, len(extra), size):
                rec = extra[i : i + size]
                code = u32(rec[0:4])
                lri = code & 0x00FFFF00
                cls = code & 0xFF
                ts = u32(rec[4:8])

                vals = (
                    [u64(rec[8:16])]
                    if size == 16
                    else [u32(rec[off : off + 4]) for off in range(8, size, 4)]
                )

                records.append((code, lri, cls, ts, vals))

            return records

    records = []
    for i in range(0, len(extra) - 11, 12):
        code = u32(extra[i : i + 4])
        records.append(
            (
                code,
                code & 0x00FFFF00,
                code & 0xFF,
                u32(extra[i + 4 : i + 8]),
                [u32(extra[i + 8 : i + 12])],
            )
        )

    return records
