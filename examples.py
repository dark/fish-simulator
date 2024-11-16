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

import numpy as np
from engine import Config, Engine, State
from randomizer import Randomizer
from typing import List


def _cartesian(array, dimensions):
    # https://stackoverflow.com/a/35608701
    all_dims = []
    for dim in range(dimensions):
        all_dims.append(array)
    return np.array(np.meshgrid(*all_dims)).T.reshape(-1, dimensions)


def _create_base_config(*, number_of_particles: int):
    r = Randomizer()
    return Config(
        v_max=5.0,
        v_decay=0.9,
        a_max=1.0,
        d_max=7.5,
        u_max=5.0,
        u1_p=1.0,
        u2_p=3.0,
        u2_dopt=1.0,
        u3_p=10.0,
        u3_dmax=3.0,
        uw=r.gen_random_matrix(
            (number_of_particles, 3),
            min_value=0.9,
            max_value=1.0,
        ),
    )


class TwoDimensionsGrid:

    _SPACE_DIMENSIONS = 2
    _PARTICLES_BY_DIM = 11

    def _create_initial_state(self):
        # Cast to int necessary to make initial spacing nicer in this
        # sample configuration.
        one_dim = np.arange(
            -(self._PARTICLES_BY_DIM / 2), self._PARTICLES_BY_DIM / 2, dtype=int
        )
        # Re-casting to float because that's what all matrices use.
        p = _cartesian(one_dim, self._SPACE_DIMENSIONS).astype(float)
        v = np.zeros_like(p)
        a = np.zeros_like(p)
        return p, v, a

    def run(self, *, timestep: float, iterations: int, **kwargs):
        p, v, a = self._create_initial_state()
        s = State(
            p,
            v,
            a,
            # This example has no predators.
            pred_p=np.zeros((0, self._SPACE_DIMENSIONS)),
            pred_v=np.zeros((0, self._SPACE_DIMENSIONS)),
            pred_a=np.zeros((0, self._SPACE_DIMENSIONS)),
        )
        cfg = _create_base_config(number_of_particles=p.shape[0])
        engine = Engine(s, cfg)
        return engine.run(
            timestep=timestep,
            iterations=iterations,
            **kwargs,
        )


class TwoDimensionsGridWithPredator(TwoDimensionsGrid):
    def run(self, *, timestep: float, iterations: int, **kwargs):
        p, v, a = self._create_initial_state()
        # Have one predator sweep from (15, 1) to (-15, 1) in the
        # first twenty seconds of the simulation.
        pred_p = np.array([[15.0, 1.0]])
        pred_v = np.array([[-1.5, 0.0]])
        pred_a = np.array([[0.0, 0.0]])
        s = State(p, v, a, pred_p, pred_v, pred_a)
        cfg = _create_base_config(number_of_particles=p.shape[0])
        engine = Engine(s, cfg)
        return engine.run(
            timestep=timestep,
            iterations=iterations,
            **kwargs,
        )


if __name__ == "__main__":
    # Run all examples and some parameter combinations.
    print(" * Running: TwoDimensionsGrid().run(timestep=0.1, iterations=100)")
    TwoDimensionsGrid().run(timestep=0.1, iterations=100)
    print(
        " * Running: TwoDimensionsGrid().run(timestep=0.1, iterations=100, skip_initial_states=25)"
    )
    TwoDimensionsGrid().run(timestep=0.1, iterations=100, skip_initial_states=25)
    print(
        " * Running: TwoDimensionsGrid().run(timestep=0.1, iterations=100, return_urgency_vectors=True)"
    )
    TwoDimensionsGrid().run(timestep=0.1, iterations=100, return_urgency_vectors=True)
    print(
        " * Running: TwoDimensionsGridWithPredator().run(timestep=0.1, iterations=100)"
    )
    TwoDimensionsGridWithPredator().run(timestep=0.1, iterations=100)
