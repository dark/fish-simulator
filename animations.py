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
from utils import Utils


def generate_dynamic_2d_axes():
    # Somehow the ratio obtained when starting with:
    #
    #   x=[-14,14], y=[-7, 7], x_length=20, y_length=10
    #
    # is aesthetically pleasing and generates square units, even
    # though the viewport really displays only x=[-10, 10], y=[-5, 5].
    #
    # The key to keep a proper square ratio is to keep
    # x.range/x.length == y.range/y.length.
    axes = Axes(
        x_range=(-14, 14, 1),
        y_range=(-7, 7, 1),
        tips=False,
        x_length=20,
        y_length=10,
        # axis_config={"include_numbers": True},
    )
    return axes


class SecondsCounter(Animation):
    def __init__(self, number: DecimalNumber, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(number, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        self.mobject.set_value(alpha)


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


class BaseTwoDimensionialScene(Scene):
    def setup(self):
        # Init editable parameters, so that we can check for them
        # later in construct(). These should be defined in the derived
        # scene.
        self._config_to_render = ...
        self._run_time = ...  # in seconds

    def construct(self):
        if self._config_to_render is Ellipsis:
            raise ValueError(
                "_config_to_render should be defined in the derived scene before construction"
            )
        if self._run_time is Ellipsis:
            raise ValueError(
                "_run_time should be defined in the derived scene before construction"
            )

        # Setup editable parameters
        run_time = self._run_time  # in seconds
        # We want to display the position of each particle, with a
        # small "trail" behind it. Duration of the trail, in seconds.
        trail_duration = 0.25

        # Determine other configuration options.
        fps = config.frame_rate
        timestep = 1 / fps
        iterations = (int)(fps * run_time)

        # Run the engine to compute all position states.
        state_histories = self._config_to_render.run(
            timestep=timestep, iterations=iterations
        )
        point_histories = Utils.repack_particle_histories_for_manim(state_histories)
        predator_histories = Utils.repack_predator_histories_for_manim(state_histories)

        # Set up a set of x,y axes.
        axes = generate_dynamic_2d_axes()
        self.add(axes)

        # Create an animation that will move a dot along the imaginary
        # path that each particle follows. We do not explicitly create
        # a path, because experimental evidence suggest that it adds a
        # lot of overhead in Manim (presumably to keep track of all
        # position states). Instead, we embed all points we expect to
        # go to directly in the animation.
        #
        # This requires that the size of the history of each point
        # (i.e. len(points_histories[x]], for each x) is equal to the
        # number for frames we want to generate + 1 (i.e. indices are
        # in the range `[0, iterations]`).
        dot_animations = []

        # Animate all particles
        colors = color_gradient([BLUE_E, BLUE_A], len(point_histories))
        for points, color in zip(point_histories, colors):
            dot = Dot(color=color, radius=0.03)
            points = axes.c2p(*points.T).T
            dot_animation = MoveAlongPoints(dot, points, run_time=run_time)
            dot_animations.append(dot_animation)

            trail = TracedPath(
                dot.get_center,
                dissipating_time=trail_duration,
                stroke_width=2.5,
                stroke_color=color,
            )
            self.add(dot, trail)

        # Animate all predators, if there are any
        if predator_histories:
            predator_colors = color_gradient([RED_E, RED_A], len(predator_histories))
            for predator_points, color in zip(predator_histories, predator_colors):
                dot = Dot(color=color, radius=0.05)
                points = axes.c2p(*predator_points.T).T
                dot_animation = MoveAlongPoints(dot, points, run_time=run_time)
                dot_animations.append(dot_animation)

                trail = TracedPath(
                    dot.get_center,
                    dissipating_time=trail_duration,
                    stroke_width=2.5,
                    stroke_color=color,
                )
                self.add(dot, trail)

        # Display a seconds timer in the top left
        seconds_text = (
            Text("Runtime:", font_size=32)
            .set_color(WHITE)
            .shift(LEFT * 6)
            .shift(UP * 3.5)
        )
        seconds_number = (
            DecimalNumber(num_decimal_places=1, unit="s")
            .set_color(WHITE)
            .next_to(seconds_text, RIGHT)
        )
        self.add(seconds_text, seconds_number)

        self.play(
            *dot_animations,
            SecondsCounter(seconds_number),
        )
