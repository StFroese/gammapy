import logging
from typing import ClassVar, Literal, Optional, Union
from pydantic import ConfigDict
from gammapy.utils.metadata import (
    METADATA_FITS_KEYS,
    CreatorMetaData,
    MetaData,
    PointingInfoMetaData,
)

__all__ = ["MapDatasetMetaData"]

MapDataset_METADATA_FITS_KEYS = {
    "MapDataset": {
        "creation": "CREATION",
        "instrument": "INSTRUM",
        "telescope": "TELESCOP",
        "observation_mode": "OBS_MODE",
        "pointing": "POINTING",
        "obs_ids": "OBS_IDS",
        "event_types": "EVT_TYPE",
        "optional": "OPTIONAL",
    },
}

METADATA_FITS_KEYS.update(MapDataset_METADATA_FITS_KEYS)


class MapDatasetMetaData(MetaData):
    """Metadata containing information about the GTI.

    Parameters
    ----------
    creation : `~gammapy.utils.CreatorMetaData`, optional
         The creation metadata.
    instrument : str
        the instrument used during observation.
    telescope : str
        The specific telescope subarray.
    observation_mode : str
        observing mode.
    pointing : ~astropy.coordinates.SkyCoord
        Telescope pointing direction.
    obs_ids : int
        Observation ids stacked in the dataset.
    event_types : int
        Event types used in analysis.
    optional : dict
        Additional optional metadata.
    """

    model_config = ConfigDict(coerce_numbers_to_str=True)

    _tag: ClassVar[Literal["MapDataset"]] = "MapDataset"
    creation: Optional[CreatorMetaData] = CreatorMetaData()
    instrument: Optional[str] = None
    telescope: Optional[Union[str, list[str]]] = None
    observation_mode: Optional[Union[str, list]] = None
    pointing: Optional[Union[PointingInfoMetaData, list[PointingInfoMetaData]]] = None
    obs_ids: Optional[Union[str, list[str]]] = None
    event_type: Optional[Union[str, list[str]]] = None
    optional: Optional[dict] = None

    def stack(self, other):
        kwargs = {}
        kwargs["creation"] = self.creation
        kwargs["instrument"] = self.instrument
        if self.instrument != other.instrument:
            logging.warning(
                f"Stacking data from different instruments {self.instrument} and {other.instrument}"
            )
        if self.telescope is not None:
            tel = self.telescope
            if isinstance(tel, str):
                tel = [tel]
            if other.telescope not in tel:
                tel.append(other.telescope)
        else:
            tel = other.telescope
        kwargs["telescope"] = tel

        if self.observation_mode is not None:
            observation_mode = self.observation_mode
            if isinstance(observation_mode, str):
                observation_mode = [observation_mode]
            observation_mode.append(other.observation_mode)
        else:
            observation_mode = other.observation_mode
        kwargs["observation_mode"] = observation_mode

        if self.pointing is not None:
            pointing = self.pointing
            if isinstance(pointing, PointingInfoMetaData):
                pointing = [pointing]
            pointing.append(other.pointing)
        else:
            pointing = other.pointing
        kwargs["pointing"] = pointing

        if self.obs_ids is not None:
            obs_ids = self.obs_ids
            if isinstance(obs_ids, str):
                obs_ids = [obs_ids]
            obs_ids.append(other.obs_ids)
        else:
            obs_ids = other.obs_ids
        kwargs["obs_ids"] = obs_ids

        if self.event_type is not None:
            event_type = self.event_type
            if isinstance(event_type, str):
                event_type = [event_type]
            event_type.append(other.event_type)
        else:
            event_type = other.event_type
        kwargs["event_type"] = event_type

        if self.optional:
            optional = self.optional
            for k in other.optional.keys():
                if not isinstance(optional[k], list):
                    optional[k] = [optional[k]]
                optional[k].append(other.optional[k])
            kwargs["optional"] = optional

        return self.__class__(**kwargs)
