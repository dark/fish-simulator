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

SPACE_DIMENSIONS = 2
FISHES_BY_DIM = 11


def cartesian(array, dimensions):
    # https://stackoverflow.com/a/35608701
    all_dims = []
    for dim in range(dimensions):
        all_dims.append(array)
    return np.array(np.meshgrid(*all_dims)).T.reshape(-1, dimensions)


def create_initial_state():
    one_dim = np.arange(-(FISHES_BY_DIM / 2), FISHES_BY_DIM / 2, dtype=int)
    p = cartesian(one_dim, SPACE_DIMENSIONS)
    v = np.zeros((FISHES_BY_DIM**2, SPACE_DIMENSIONS))
    a = np.zeros((FISHES_BY_DIM**2, SPACE_DIMENSIONS))
    return p, v, a


def create_config():
    r = Randomizer()
    return Config(
        a_max=1.0,
        d_max=5.0,
        u1_p=1.0,
        u2_p=1.0,
        u2_dopt=1.0,
        u4=2.0,
        uw=r.gen_epsilon_matrix((FISHES_BY_DIM, 4)),
    )


p, v, a = create_initial_state()
s = State(p, v, a)
cfg = create_config()
engine = Engine(s, cfg)
