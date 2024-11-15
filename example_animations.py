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

from manim import *
from animations import BaseTwoDimensionialScene
from examples import TwoDimensionsGrid, TwoDimensionsGridWithPredator


class TwoDimensionsGridDisplay(BaseTwoDimensionialScene):
    def setup(self):
        super().setup()
        self._config_to_render = TwoDimensionsGrid()
        self._render_run_time = 30
        self._do_not_render_initial_seconds = 0
        self._exemplar_indices = {0, 10, 110, 120}
        self._exemplar_info = self.ExemplarInfo.ACCELERATION

    def construct(self):
        super().construct()


class TwoDimensionsGridWithPredatorDisplay(BaseTwoDimensionialScene):
    def setup(self):
        super().setup()
        self._config_to_render = TwoDimensionsGridWithPredator()
        self._render_run_time = 30
        self._do_not_render_initial_seconds = 0
        self._exemplar_indices = {0, 10, 110, 120}
        self._exemplar_info = self.ExemplarInfo.ACCELERATION

    def construct(self):
        super().construct()
