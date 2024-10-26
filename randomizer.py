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
from typing import Tuple


EPSILON = 0.001
SEED = 133713371337


class Randomizer:
    def __init__(self):
        self._rng = np.random.default_rng(seed=SEED)

    def gen_epsilon_matrix(self, shape: Tuple):
        return self.gen_random_matrix(
            shape, min_value=1.0 - EPSILON, max_value=1.0 + EPSILON
        )

    def gen_random_matrix(self, shape: Tuple, *, min_value: float, max_value: float):
        return (max_value - min_value) * self._rng.random(size=shape) + min_value
