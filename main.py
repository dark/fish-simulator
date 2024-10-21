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
import scipy

SPACE_DIMENSIONS = 2


def cartesian(array, dimensions):
    # https://stackoverflow.com/a/35608701
    all_dims = []
    for dim in range(dimensions):
        all_dims.append(array)
    return np.array(np.meshgrid(*all_dims)).T.reshape(-1, dimensions)


def create_initial_state():
    FISHES_BY_DIM = 11

    one_dim = np.arange(-(FISHES_BY_DIM / 2), FISHES_BY_DIM / 2, dtype=int)
    p = cartesian(one_dim, SPACE_DIMENSIONS)
    v = np.zeros((11**2, SPACE_DIMENSIONS))
    a = np.zeros((11**2, SPACE_DIMENSIONS))
    return p, v, a


p, v, a = create_initial_state()
print(p)
