"""UDP API client for Marstek Venus A."""
from __future__ import annotations

import asyncio
import json
import socket
from collections.abc import Mapping
from typing import Any

from .const import (
    METHOD_BAT_STATUS,
    METHOD_EM_STATUS,
    METHOD_ES_MODE,
    METHOD_ES_STATUS,
    METHOD_PV_STATUS,
    METHOD_WIFI_STATUS,
)


class MarstekApiError(Exception):
    """Raised when the Marstek API fails."""


class MarstekVenusAApi:
    """Simple UDP JSON-RPC client for Marstek Venus A."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._request_id = 0

    async def async_fetch_all(self, pv1_factor: float) -> dict[str, Any]:
        """Fetch the validated live values used by the integration."""
        es = await self._async_request(METHOD_ES_STATUS)
        pv = await self._async_request(METHOD_PV_STATUS)
        bat = await self._async_request(METHOD_BAT_STATUS)
        em = await self._async_request(METHOD_EM_STATUS)
        mode = await self._async_request(METHOD_ES_MODE)
        wifi = await self._async_request(METHOD_WIFI_STATUS)

        def pv_power(index: int) -> float:
            raw = pv.get(f"pv{index}_power", 0)
            if index == 1:
                return round(float(raw) * pv1_factor, 2)
            return float(raw)

        return {
            "battery_soc": es.get("bat_soc", bat.get("soc")),
            "battery_capacity_wh": es.get("bat_cap"),
            "battery_temperature": bat.get("bat_temp"),
            "pv1_power": pv_power(1),
            "pv2_power": pv_power(2),
            "pv3_power": pv_power(3),
            "pv4_power": pv_power(4),
            "pv_power_total": round(pv_power(1) + pv_power(2) + pv_power(3) + pv_power(4), 2),
            "grid_power": es.get("ongrid_power"),
            "offgrid_power": es.get("offgrid_power"),
            "meter_total_power": em.get("total_power"),
            "total_grid_output_energy_wh": es.get("total_grid_output_energy"),
            "total_grid_input_energy_wh": es.get("total_grid_input_energy"),
            "operating_mode": mode.get("mode", "unknown"),
            "wifi_rssi": wifi.get("rssi"),
            "raw": {
                METHOD_ES_STATUS: es,
                METHOD_PV_STATUS: pv,
                METHOD_BAT_STATUS: bat,
                METHOD_EM_STATUS: em,
                METHOD_ES_MODE: mode,
                METHOD_WIFI_STATUS: wifi,
            },
        }

    async def _async_request(self, method: str) -> Mapping[str, Any]:
        """Perform one UDP JSON-RPC request."""
        return await asyncio.to_thread(self._request, method)

    def _request(self, method: str) -> Mapping[str, Any]:
        self._request_id += 1
        payload = {
            "id": self._request_id,
            "method": method,
            "params": {"id": 0},
        }

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.settimeout(2.5)
                sock.bind(("0.0.0.0", self._port))
                sock.sendto(json.dumps(payload).encode("utf-8"), (self._host, self._port))
                data, _remote = sock.recvfrom(8192)
        except TimeoutError as err:
            raise MarstekApiError(f"Timeout while calling {method}") from err
        except OSError as err:
            raise MarstekApiError(f"Socket error while calling {method}: {err}") from err

        try:
            response = json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as err:
            raise MarstekApiError(f"Invalid JSON while calling {method}") from err

        if "error" in response:
            raise MarstekApiError(response["error"].get("message", f"{method} failed"))
        return response.get("result", {})
