"""Data coordinator for Marstek Venus A Local."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MarstekApiError, MarstekVenusAApi
from .const import (
    CONF_DEVICE_HOST,
    CONF_PV1_FACTOR,
    CONF_SCAN_INTERVAL,
    CONF_UDP_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class MarstekVenusALocalCoordinator(DataUpdateCoordinator[dict]):
    """Coordinator for Venus A Local data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.api = MarstekVenusAApi(
            host=entry.data[CONF_DEVICE_HOST],
            port=entry.data[CONF_UDP_PORT],
        )
        interval_seconds = entry.options.get(
            CONF_SCAN_INTERVAL,
            int(DEFAULT_SCAN_INTERVAL.total_seconds()),
        )
        super().__init__(
            hass,
            logger=logging.getLogger(__name__),
            name=f"{DOMAIN}_{entry.title}",
            update_interval=timedelta(seconds=interval_seconds),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from Venus A."""
        try:
            return await self.api.async_fetch_all(
                pv1_factor=self.entry.options.get(CONF_PV1_FACTOR, self.entry.data[CONF_PV1_FACTOR])
            )
        except MarstekApiError as err:
            raise UpdateFailed(str(err)) from err
