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

import enum
from manim import *


class SecondsCounter(Animation):
    def __init__(self, number: DecimalNumber, begin: int, end: int, **kwargs) -> None:
        self._begin = begin
        self._end = end
        # Pass number as the mobject of the animation
        super().__init__(number, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        self.mobject.set_value(self._begin + alpha * (self._end - self._begin))


class MoveAlongPoints(Animation):
    """
    Move a Mobject exactly along the points provided.
    """

    def __init__(
        self,
        mobject: Mobject,
        points: np.typing.NDArray,
        **kwargs,
    ) -> None:
        self._points = points
        self._last_index = len(points) - 1
        # Pass provided mobject as the mobject of the animation
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        # The goal is to return the point from `self._points` at the
        # right index in `[0, last_index]` based on
        # `alpha*len(points)`. Due to floating point math, rounding is
        # expected.
        self.mobject.move_to(self._points[round(alpha * self._last_index)])


class MoveLineBetweenPoints(Animation):
    """
    Move a Line object (or any derived class) between the points provided.
    """

    def __init__(
        self,
        mobject: Line,
        start_points: np.typing.NDArray,
        end_points: np.typing.NDArray,
        **kwargs,
    ) -> None:
        self._start_points = start_points
        self._end_points = end_points
        self._last_index = len(start_points) - 1
        if len(start_points) != len(end_points):
            raise ValueError(
                "Inconsistent array lengths: {} and {}".format(
                    len(start_points), len(end_points)
                )
            )

        # Pass provided mobject as the mobject of the animation
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        # The goal is to return the point from `self._start_points` at
        # the right index in `[0, last_index]` based on
        # `alpha*len(points)`. Same for `self._end_points`.
        #
        # Due to floating point math, rounding is expected.
        start = self._start_points[round(alpha * self._last_index)]
        end = self._end_points[round(alpha * self._last_index)]
        self.mobject.put_start_and_end_on(start, end)
