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

import numpy as np
from engine import Config, Engine, State
from randomizer import Randomizer
from typing import List


def cartesian(array, dimensions):
    # https://stackoverflow.com/a/35608701
    all_dims = []
    for dim in range(dimensions):
        all_dims.append(array)
    return np.array(np.meshgrid(*all_dims)).T.reshape(-1, dimensions)


class TwoDimensionsGrid:

    SPACE_DIMENSIONS = 2
    FISHES_BY_DIM = 11

    def _create_initial_state(self):
        # Cast to int necessary to make initial spacing nicer in this
        # sample configuration.
        one_dim = np.arange(
            -(self.FISHES_BY_DIM / 2), self.FISHES_BY_DIM / 2, dtype=int
        )
        # Re-casting to float because that's what all matrices use.
        p = cartesian(one_dim, self.SPACE_DIMENSIONS).astype(float)
        v = np.zeros((self.FISHES_BY_DIM**self.SPACE_DIMENSIONS, self.SPACE_DIMENSIONS))
        a = np.zeros((self.FISHES_BY_DIM**self.SPACE_DIMENSIONS, self.SPACE_DIMENSIONS))
        return p, v, a

    def _create_config(self):
        r = Randomizer()
        return Config(
            v_max=1.0,
            a_max=1.0,
            d_max=1.0,
            u_max=1.0,
            u1_p=1.0,
            u2_p=1.0,
            u2_dopt=1.0,
            u4=2.0,
            uw=r.gen_random_matrix(
                (self.FISHES_BY_DIM**self.SPACE_DIMENSIONS, 4),
                min_value=0.9,
                max_value=1.0,
            ),
        )

    def run(self, *, timestep: float, iterations: int):
        p, v, a = self._create_initial_state()
        s = State(p, v, a)
        cfg = self._create_config()
        engine = Engine(s, cfg)
        return engine.run(timestep=timestep, iterations=iterations)


if __name__ == "__main__":
    # Run and print this example by default.
    result = TwoDimensionsGrid().run(timestep=0.1, iterations=300)
    print(result)
