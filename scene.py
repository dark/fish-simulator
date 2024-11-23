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
from animation import MoveAlongPoints, MoveLineBetweenPoints, SecondsCounter
from manim import *
from util import Utils
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


def _generate_axes(p_histories):
    """Generates a set of axes based on spatial dimensions."""
    x_axes_minmax = (
        min([min(p[:, 0]) for p in p_histories]),
        max([max(p[:, 0]) for p in p_histories]),
    )
    y_axes_minmax = (
        min([min(p[:, 1]) for p in p_histories]),
        max([max(p[:, 1]) for p in p_histories]),
    )
    return _generate_dynamic_2d_axes(x_axes_minmax, y_axes_minmax)


class BaseSceneMixin:
    class ExemplarInfo(enum.Enum):
        NONE = 0
        ACCELERATION = 1
        URGENCIES = 2

    def setup(self):
        # Init editable parameters, so that we can check for them
        # later in construct(). These should be defined in the derived
        # scene.
        self._config_to_render = ...
        # Render runtime, in seconds.
        self._render_run_time = ...

        # Init optional parameters with their default values.

        # The time, in seconds, that will be simulated, but not
        # rendered, at the beginning of the simulation.
        self._do_not_render_initial_seconds = 0
        # Whether the runtime counter at the top left of the animation
        # should include the time portion of the simulation that was
        # simulated, but not rendered. If False, the counter will
        # always start at zero.
        self._runtime_counter_includes_prelude = False
        # Which particles will be used as exemplars.
        self._exemplar_indices = {}
        # What information will be displayed for exemplars.
        self._exemplar_info = self.ExemplarInfo.NONE
        # How much the value displayed for each exemplar will be
        # rescaled. Useful to display smaller-scale values.
        self._exemplar_amplification = 1.0

    def construct(self):
        if self._config_to_render is Ellipsis:
            raise ValueError(
                "_config_to_render should be defined in the derived scene before construction"
            )
        if self._render_run_time is Ellipsis:
            raise ValueError(
                "_render_run_time should be defined in the derived scene before construction"
            )

        # Setup editable parameters
        total_run_time = self._render_run_time + self._do_not_render_initial_seconds
        render_run_time = self._render_run_time
        # We want to display the position of each particle, with a
        # small "trail" behind it. Duration of the trail, in seconds.
        trail_duration = 0.25

        # Determine other configuration options.
        fps = config.frame_rate
        timestep = 1 / fps
        iterations = (int)(fps * total_run_time)
        skip_initial_iterations = (int)(fps * self._do_not_render_initial_seconds)
        print(
            "Configuration: fps={} timestep={}, total(runtime,iterations)={},{} render(runtime,iterations)={},{}".format(
                fps,
                timestep,
                total_run_time,
                iterations,
                render_run_time,
                iterations - skip_initial_iterations,
            )
        )

        # Run the engine to compute all position states.
        results = self._config_to_render.run(
            timestep=timestep,
            iterations=iterations,
            skip_initial_states=skip_initial_iterations,
            return_urgency_vectors=(self._exemplar_info == self.ExemplarInfo.URGENCIES),
        )
        p_histories, _, a_histories = Utils.repack_particle_histories_for_manim(
            results.states
        )
        predator_histories = Utils.repack_predator_histories_for_manim(results.states)

        # Set up the axes.
        axes = _generate_axes(p_histories)
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
            dot_animation = MoveAlongPoints(
                dot, axes_p_points, run_time=render_run_time
            )
            animations.append(dot_animation)

            trail = TracedPath(
                dot.get_center,
                dissipating_time=trail_duration,
                stroke_width=2.5,
                stroke_color=color,
            )
            self.add(dot, trail)

            if idx in self._exemplar_indices:
                if self._exemplar_info == self.ExemplarInfo.ACCELERATION:
                    # For the purpose of drawing acceleration vectors,
                    # the starting points are the Dot positions, while
                    # the end points are where the acceleration vector
                    # ends, when added.
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
                        line, axes_p_points, axes_a_ends, run_time=render_run_time
                    )
                    animations.append(line_animation)
                    self.add(line)
                elif self._exemplar_info == self.ExemplarInfo.URGENCIES:
                    # Here we want to display, for each exemplar, as
                    # many lines as there are urgencies.
                    urgencies = (
                        self._exemplar_amplification
                        * Utils.repack_one_particle_urgencies_for_manim(
                            idx, results.urgencies
                        )
                    )
                    urgencies_count = urgencies.shape[0]
                    urgency_colors = [YELLOW, PURPLE, RED]
                    for urgency_idx, urgency_color in zip(
                        range(urgencies_count), urgency_colors, strict=True
                    ):
                        u_ends = urgencies[urgency_idx, :] + p_points
                        axes_urgency_ends = axes.c2p(*u_ends.T).T

                        urgency_line = Line(
                            stroke_width=1.5,
                            buff=0,
                            color=urgency_color,
                            start=axes_p_points[0],
                            end=axes_urgency_ends[0],
                        )
                        urgency_line_animation = MoveLineBetweenPoints(
                            urgency_line,
                            axes_p_points,
                            axes_urgency_ends,
                            run_time=render_run_time,
                        )
                        animations.append(urgency_line_animation)
                        self.add(urgency_line)

        # Animate all predators, if there are any
        if predator_histories:
            predator_colors = color_gradient([RED_E, RED_A], len(predator_histories))
            for predator_points, color in zip(predator_histories, predator_colors):
                axes_p_points = axes.c2p(*predator_points.T).T

                dot = Dot(color=color, radius=0.05)
                dot_animation = MoveAlongPoints(
                    dot, axes_p_points, run_time=render_run_time
                )
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
            SecondsCounter(
                seconds_number,
                begin=(
                    self._do_not_render_initial_seconds
                    if self._runtime_counter_includes_prelude
                    else 0
                ),
                end=(
                    total_run_time
                    if self._runtime_counter_includes_prelude
                    else render_run_time
                ),
                run_time=render_run_time,
            ),
        )


class BaseTwoDimensionialScene(BaseSceneMixin, Scene):
    pass
