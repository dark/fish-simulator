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

from manim import *
from examples import TwoDimensionsGrid
from utils import Utils


class TwoDimensionsGridDisplay(Scene):
    def construct(self):
        # Set up a set of x,y axes. The key to keep a proper square
        # ratio is to keep x.range/x.length == y.range/y.length.
        axes = Axes(
            x_range=(-14, 14, 1),
            y_range=(-7, 7, 1),
            tips=False,
            x_length=20,
            y_length=10,
            # axis_config={ "include_numbers": True},
        )
        self.add(axes)

        # Run the engine to compute all position states.
        timestep = 0.1
        iterations = 300
        run_time = timestep * iterations
        state_histories = TwoDimensionsGrid().run(
            timestep=timestep, iterations=iterations
        )
        point_histories = Utils.repack_state_histories_for_manim(state_histories)

        # Define a curve for each actor in the simulation, and give it a unique color
        curves = VGroup()
        colors = color_gradient([BLUE_E, BLUE_A], len(point_histories))
        for points, color in zip(point_histories, colors):
            curve = VMobject().set_points_smoothly(axes.c2p(*points.T).T)
            curve.set_stroke(color, 3, opacity=1)
            curves.add(curve)

        # We want to display the position of each actor, with a small
        # "trail" behind it.
        #
        # Duration of the trail, in seconds.
        trail_duration = 0.25
        # How long the trail is compared to the overall runtime
        trail_ratio = trail_duration / run_time

        # Slightly extend the duration of the overall animation, to
        # account for the time needed to fade out the trail at the end.
        self.play(
            *(
                ShowPassingFlash(
                    curve,
                    time_width=trail_ratio,
                    rate_func=linear,
                    run_time=run_time + trail_duration,
                )
                for curve in curves
            ),
        )
