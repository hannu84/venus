"""Constants for Marstek Venus A Local."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "marstek_venus_a_local"

CONF_DEVICE_HOST = "device_host"
CONF_UDP_PORT = "udp_port"
CONF_PV1_FACTOR = "pv1_power_factor"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_UDP_PORT = 30000
DEFAULT_PV1_FACTOR = 0.1
DEFAULT_SCAN_INTERVAL = timedelta(seconds=10)

MANUFACTURER = "Marstek"
MODEL = "Venus A"

METHOD_ES_STATUS = "ES.GetStatus"
METHOD_PV_STATUS = "PV.GetStatus"
METHOD_BAT_STATUS = "Bat.GetStatus"
METHOD_EM_STATUS = "EM.GetStatus"
METHOD_ES_MODE = "ES.GetMode"
METHOD_WIFI_STATUS = "Wifi.GetStatus"
