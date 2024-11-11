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
from typing import Tuple


def _generate_2d_axis_range(
    minmax: Tuple[float, float], length: float, buffer_factor: float
):
    midpoint = (minmax[1] + minmax[0]) / 2
    return (
        midpoint - length * buffer_factor / 2,
        midpoint + length * buffer_factor / 2,
        1,
    )


def _generate_dynamic_2d_axes(
    x_axes_minmax: Tuple[float, float], y_axes_minmax: Tuple[float, float]
):
    """Generates a dynamic set of axes.

    This takes into consideration the min/max values the points to be
    displayed have on either axis.

    """

    # Somehow the ratio obtained when starting with:
    #
    #   x=[-14,14], y=[-7, 7], x_length=20, y_length=10
    #
    # is aesthetically pleasing and generates square units, even
    # though the viewport really displays only x=[-9.5, 9.5], y=[-5, 5].
    #
    # Also, the key to keep a proper square ratio is to keep
    # x.range/x.length == y.range/y.length.

    # The minimum length of 19 corresponds to the x=[-9.5, 9.5] viewport.
    smallest_viewport_length_x = max(x_axes_minmax[1] - x_axes_minmax[0], 19.0)
    # The minimum length of 10 corresponds to the y=[-5, 5] viewport.
    smallest_viewport_length_y = max(y_axes_minmax[1] - y_axes_minmax[0], 10.0)

    # Check which viewport needs to widen to maintain the pleasing
    # ratio mentioned above.
    if smallest_viewport_length_x / smallest_viewport_length_y < 1.9:
        # Stretch the x length to match
        viewport_length_x = smallest_viewport_length_y * 1.9
        viewport_length_y = smallest_viewport_length_y
    else:
        # Stretch the y length to match
        viewport_length_x = smallest_viewport_length_x
        viewport_length_y = smallest_viewport_length_x / 1.9

    print(
        "Using dynamic viewport with ratio x:y={}:{}".format(
            viewport_length_x, viewport_length_y
        )
    )
    # The buffer factor would give a range of x=[-14, 14] for viewport
    # x=[-9.5, 9.5].
    x_range = _generate_2d_axis_range(x_axes_minmax, viewport_length_x, 28.0 / 19.0)
    # The buffer factor would give a range of y=[-7, 7] for viewport
    # y=[-5, 5].
    y_range = _generate_2d_axis_range(y_axes_minmax, viewport_length_y, 14.0 / 10.0)
    print("Using x axis range: {}".format(x_range))
    print("Using y axis range: {}".format(y_range))

    # These are constant to maintain the ratio obtained at the top,
    # and still keep the entire viewport visible.
    x_length = 20
    y_length = 10
    print("Using lengths: x={} y={}".format(x_length, y_length))

    return Axes(
        x_range=x_range,
        y_range=y_range,
        tips=False,
        x_length=x_length,
        y_length=y_length,
        # axis_config={"include_numbers": True},
    )


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


class BaseTwoDimensionialScene(Scene):
    def setup(self):
        # Init editable parameters, so that we can check for them
        # later in construct(). These should be defined in the derived
        # scene.
        self._config_to_render = ...
        self._run_time = ...  # in seconds

        # Init optional parameters with their default values.

        # Which particles will be used as exemplars.
        self._exemplar_indices = {}
        # How much the value displayed for each exemplar will be
        # rescaled. Useful to display smaller-scale values.
        self._exemplar_amplification = 1.0

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
        p_histories, _, a_histories = Utils.repack_particle_histories_for_manim(
            state_histories
        )
        predator_histories = Utils.repack_predator_histories_for_manim(state_histories)

        # Set up a set of x,y axes.
        x_axes_minmax = (
            min([min(p[:, 0]) for p in p_histories]),
            max([max(p[:, 0]) for p in p_histories]),
        )
        y_axes_minmax = (
            min([min(p[:, 1]) for p in p_histories]),
            max([max(p[:, 1]) for p in p_histories]),
        )
        axes = _generate_dynamic_2d_axes(x_axes_minmax, y_axes_minmax)
        self.add(axes)

        # Create an animation that will move a dot along the imaginary
        # path that each particle follows. We do not explicitly create
        # a path, because experimental evidence suggest that it adds a
        # lot of overhead in Manim (presumably to keep track of all
        # position states). Instead, we embed all points we expect to
        # go to directly in the animation.
        #
        # This requires that the size of the history of each point
        # (i.e. len(p_histories[x]], for each x) is equal to the
        # number for frames we want to generate + 1 (i.e. indices are
        # in the range `[0, iterations]`).
        animations = []

        # Animate all particles
        colors = color_gradient([BLUE_E, BLUE_A], len(p_histories))
        for idx, p_points, a_points, color in zip(
            range(len(p_histories)), p_histories, a_histories, colors, strict=True
        ):
            # Convert the position points to the frame of reference
            # defined by the axes.
            axes_p_points = axes.c2p(*p_points.T).T

            dot = Dot(color=color, radius=0.03)
            dot_animation = MoveAlongPoints(dot, axes_p_points, run_time=run_time)
            animations.append(dot_animation)

            trail = TracedPath(
                dot.get_center,
                dissipating_time=trail_duration,
                stroke_width=2.5,
                stroke_color=color,
            )
            self.add(dot, trail)

            # For the purpose of drawing acceleration vectors, the
            # starting points are the Dot positions, while the end
            # points are where the acceleration vector ends, when
            # added.
            if idx in self._exemplar_indices:
                a_ends = a_points * self._exemplar_amplification + p_points
                axes_a_ends = axes.c2p(*a_ends.T).T

                line = Line(
                    stroke_width=1,
                    buff=0,
                    color=color,
                    start=axes_p_points[0],
                    end=axes_a_ends[0],
                )
                line_animation = MoveLineBetweenPoints(
                    line, axes_p_points, axes_a_ends, run_time=run_time
                )
                animations.append(line_animation)
                self.add(line)

        # Animate all predators, if there are any
        if predator_histories:
            predator_colors = color_gradient([RED_E, RED_A], len(predator_histories))
            for predator_points, color in zip(predator_histories, predator_colors):
                dot = Dot(color=color, radius=0.05)
                points = axes.c2p(*predator_points.T).T
                dot_animation = MoveAlongPoints(dot, points, run_time=run_time)
                animations.append(dot_animation)

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
            *animations,
            SecondsCounter(seconds_number),
        )
