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


class Utils:
    def inplace_clip_by_abs(input: np.typing.NDArray, max_abs: float):
        """Clips rows of a (n, d) matrix so that abs(row)<=max_abs."""
        sum_of_squares = np.sum(input**2, axis=1, keepdims=1)
        clipped = sum_of_squares > (max_abs**2)
        scale_factors = np.ones_like(sum_of_squares)
        scale_factors[clipped] = np.sqrt(sum_of_squares[clipped]) / max_abs
        np.divide(input, scale_factors, out=input, where=clipped)
