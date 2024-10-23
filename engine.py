#!/usr/bin/python3
#
#  Simulate and display movement of a fish school
#  Copyright (C) 2024  Marco Leogrande
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import attrs
import numpy as np
from randomizer import Randomizer


@attrs.define
class State:
    p: np.typing.NDArray  # (n, d) vector of position state
    v: np.typing.NDArray  # (n, d) vector of velocity state
    a: np.typing.NDArray  # (n, d) vector of acceleration state


@attrs.frozen(kw_only=True)
class Config:
    # Species-wide config
    a_max: float  # max linear acceleration (species-wide)
    d_max: float  # max sight distance (species-wide)
    u1_p: float  # linear parameter for the 1st urgency component (species-wide)
    u2_p: float  # linear parameter for the 2nd urgency component (species-wide)
    u2_dopt: float  # optimal distance for the 2nd urgency component (species-wide)
    u4: float  # linear parameter for the 4th urgency component (species-wide)
    # Per-individual config
    uw: np.typing.NDArray  # (n, 4) weights for each urgency component (per-individual)


class Engine:
    _state: State
    _cfg: Config
    _rand: Randomizer

    def __init__(self, state: State, cfg: Config):
        self._state = state
        self._cfg = cfg
        self._rand = Randomizer()

        ## sanity checks
        if (
            self._state.p.shape != self._state.v.shape
            or self._state.p.shape != self._state.a.shape
            or self._cfg.uw.shape != (self._state.p.shape[0], 4)
        ):
            raise ValueError(
                "Inconsistent shapes: p={0} v={1} a={2} uw={3}".format(
                    self._state.p.shape,
                    self._state.v.shape,
                    self._state.a.shape,
                    self._cfg.uw.shape,
                )
            )
