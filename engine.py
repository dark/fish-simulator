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
import math
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
    v_decay: float  # exponential decay parameter for the velocity vector (species-wide)
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
            if iteration % 10 == 9:
                print("Simulating iteration {}/{}".format(iteration + 1, iterations))
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
        self._state.v *= math.pow(self._cfg.v_decay, timestep)
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
        # is a (n, d) matrix.
        baricenters = weights @ self._state.p
        # Calculate the vector first (with epsilson)
        u1_vector = (baricenters - self._state.p) * self._rand.gen_epsilon_matrix(
            self._state.p.shape
        )
        # Multiply by the appropriate weights.
        return u1_vector * self._cfg.u1_p * self._cfg.uw[:, 0].reshape((-1, 1))

    def _calculate_urgency2(self, distances):
        """
        Avoids each particle from getting too close to other particles.
        """
        # Select all particles that, for this component, have an
        # effect on one another.
        in_range = np.logical_and(distances > 0, distances <= self._cfg.u2_dopt)
        # Generate weights for how much each particle affects another.
        weights = np.zeros_like(in_range, dtype=float)
        # The weight formula is:
        #
        # weight = desired_length / initial_length
        #        = ((_cfg.u2_dopt - initial_length)/_cfg.u2_dopt) / initial_length
        #        = (_cfg.u2_dopt - initial_length) / (_cfg.u2_dopt * initial_length)
        np.divide(
            self._cfg.u2_dopt - distances,
            self._cfg.u2_dopt * distances,
            where=in_range,
            out=weights,
        )
        # The weights need to be applied to the distance vector
        # existing between each pair of particles. Hence, we need to
        # compute all such vector distances.
        #
        # This results in a (n, n, d) matrix.
        #
        # Note also that the difference is computed as (particle -
        # other_particle), because this is a repulsive force: the
        # vector points from the other particle to the given one. The
        # way which Numpy broadcasting works, this requires
        # "extending" the first array, so we can keep `particle`
        # constant while we "iterate" over `other_particle`.
        distance_vectors = self._state.p[:, np.newaxis] - self._state.p

        # Calculate the total effect on each particle (with
        # epsilson). The operation applies a matrix multiplication
        # separately on each last two dimensions. In other words:
        #
        # (n, a, b) * (n, b, c) -> (n, a, c)
        #
        # for each of the n matrices in the leftmost dimension, compute:
        #
        # (a, b) @ (b, c) = (a, c)
        #
        # See also:
        # https://numpy.org/devdocs/reference/routines.linalg.html#linear-algebra-on-several-matrices-at-once
        #
        # This requires some reshaping on the fly to make dimensions work.
        number_of_points = self._state.p.shape[0]
        u2_vector = np.matmul(
            weights.reshape((number_of_points, 1, number_of_points)), distance_vectors
        ).reshape(number_of_points, -1) * self._rand.gen_epsilon_matrix(
            self._state.p.shape
        )
        # Multiply by the appropriate weights.
        return u2_vector * self._cfg.u2_p * self._cfg.uw[:, 1].reshape((-1, 1))

    def _calculate_urgency4(self, distances):
        """
        Repels each particle from specially-designated "predactor" particles.
        """
        # stub
        return np.zeros_like(self._state.a)
