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
from typing import List, Tuple


class Utils:
    def inplace_clip_by_abs(input: np.typing.NDArray, max_abs: float):
        """Clips row values of a (n, d) matrix so that abs(row)<=max_abs."""
        sum_of_squares = np.sum(input**2, axis=1, keepdims=1)
        clipped = sum_of_squares > (max_abs**2)
        scale_factors = np.ones_like(sum_of_squares)
        scale_factors[clipped] = np.sqrt(sum_of_squares[clipped]) / max_abs
        np.divide(input, scale_factors, out=input, where=clipped)

    def repack_particle_histories_for_manim(
        state_history: "List[State]",
    ) -> Tuple[
        List[np.typing.NDArray], List[np.typing.NDArray], List[np.typing.NDArray]
    ]:
        """Repacks a list of particle state histories to be used by Manim.

        Engine operations return a list of entries, where each entry
        is the state of the engine at that iteration. Manim requires
        instead a different list, where each entry represents all the
        positions that a specific particle went through in the
        simulation.

        This method converts from the former to the latter format,
        returning the position, velocity and acceleration vectors
        separately.

        """
        p_histories = []
        v_histories = []
        a_histories = []
        number_of_particles = len(state_history[0].p)
        for idx in range(0, number_of_particles):
            p_histories.append(np.array([s.p[idx] for s in state_history]))
            v_histories.append(np.array([s.v[idx] for s in state_history]))
            a_histories.append(np.array([s.a[idx] for s in state_history]))
        return p_histories, v_histories, a_histories

    def repack_one_particle_urgencies_for_manim(
        idx: int, urgencies_histories: List[np.typing.NDArray]
    ) -> np.typing.NDArray:
        """Repacks a list of urgency histories to be used by Manim.

        Engine operations return a list of entries, where each entry
        is the state of the urgencies at each iteration, with shape
        (urgencies_count, particles_count, dimensions_count).

        This method extract the urgencies for a specific particle,
        returning them in an array with shape
        (urgencies_count, iterations_count, dimensions_count).

        """
        result = np.zeros(
            (
                urgencies_histories[0].shape[0],
                len(urgencies_histories),
                urgencies_histories[0].shape[2],
            )
        )
        for snap_idx, snapshot in enumerate(urgencies_histories):
            result[:, snap_idx, :] = snapshot[:, idx, :]
        return result

    def repack_predator_histories_for_manim(
        state_history: "List[State]",
    ) -> List[np.typing.NDArray]:
        """Repacks a list of predator state histories to be used by Manim.

        Like `repack_particle_histories_for_manim`, but for predators.
        """
        predator_histories = []
        number_of_predators = len(state_history[0].pred_p)
        for idx in range(0, number_of_predators):
            array = np.array([s.pred_p[idx] for s in state_history])
            predator_histories.append(array)
        return predator_histories
