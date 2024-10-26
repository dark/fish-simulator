#!/usr/bin/python3
#
#  Simulate and display movement of particles in a system
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
import copy
import numpy as np
import scipy
from utils import Utils
from randomizer import Randomizer
from typing import List


@attrs.define
class State:
    p: np.typing.NDArray  # (n, d) vector of position state
    v: np.typing.NDArray  # (n, d) vector of velocity state
    a: np.typing.NDArray  # (n, d) vector of acceleration state


@attrs.frozen(kw_only=True)
class Config:
    # Species-wide config
    v_max: float  # max linear velocity (species-wide)
    a_max: float  # max linear acceleration (species-wide)
    d_max: float  # max sight distance (species-wide)
    u_max: float  # urgency value (absolute) that corresponds to a_max (species-wide)
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

    def run(self, *, timestep: float, iterations: int) -> List[State]:
        """Run the simulation, return a snapshot of all states."""
        states = [copy.deepcopy(self._state)]
        for iteration in range(iterations):
            current_time = timestep * iteration
            print(
                "Excuting iteration {}/{}, time: {}s".format(
                    iteration + 1, iterations, current_time
                )
            )
            self._step(timestep)
            states.append(copy.deepcopy(self._state))
        return states

    def _step(self, timestep: float):
        """Execute one step of the simulation."""
        distances = scipy.spatial.distance.squareform(
            scipy.spatial.distance.pdist(self._state.p)
        )
        # Calculate every single urgency
        u1 = self._calculate_urgency1(distances)
        u2 = self._calculate_urgency2(distances)
        u4 = self._calculate_urgency4(distances)
        # Calculate and clip the total urgency
        u_tot = u1 + u2 + u4
        self._state.a = u_tot / self._cfg.u_max * self._cfg.a_max
        Utils.inplace_clip_by_abs(self._state.a, self._cfg.a_max)
        # Add epsilon uncertainty to final acceleration matrix
        self._state.a *= self._rand.gen_epsilon_matrix(self._state.a.shape)
        # Edit velocity and position state accordingly
        self._state.v += self._state.a * timestep
        Utils.inplace_clip_by_abs(self._state.v, self._cfg.v_max)
        self._state.p += self._state.v * timestep

    def _calculate_urgency1(self, distances):
        """
        Attracts each particle to the baricenter of the other particles in range.
        """
        # Select all particles that, for this component, have an
        # effect on one another.
        in_range = np.logical_and(distances > 0, distances <= self._cfg.d_max)
        # To calculate the baricenter that each particle is affected
        # by, generate a weights matrix first. This matrix embeds how
        # much each other particle contributes to the final baricenter
        # experienced by any given particle.
        weights = np.zeros_like(in_range, dtype=float)
        np.divide(
            1.0,
            np.count_nonzero(in_range, axis=1, keepdims=1),
            where=in_range,
            out=weights,
        )
        # Calculate the baricenter as witnessed by each particle. This
        # is a (d, n) matrix.
        baricenters = self._state.p.T @ weights.T
        # Calculate the vector first (with epsilson)
        u1_vector = (baricenters.T - self._state.p) * self._rand.gen_epsilon_matrix(
            self._state.p.shape
        )
        # Multiply by the appropriate weights.
        return u1_vector * self._cfg.u1_p * self._cfg.uw[:, 0].reshape((-1, 1))

    def _calculate_urgency2(self, distances):
        """
        Avoids each particle from getting too close to other particles.
        """
        # stub
        return np.zeros_like(self._state.a)

    def _calculate_urgency4(self, distances):
        """
        Repels each particle from specially-designated "predactor" particles.
        """
        # stub
        return np.zeros_like(self._state.a)
