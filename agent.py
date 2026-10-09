
"""A small Days at Three Branches starter built entirely from sandbox.village."""

from sandbox.observation_types import ThreeBranchesAction, ThreeBranchesObservation
from sandbox.village import action, geometry, layout, me, people, props


def _cell_centre(cell: dict[str, int]) -> dict[str, float]:
    """Return the point at the centre of one village cell."""
    return {"x": cell["x"] + 0.5, "y": cell["y"] + 0.5}


class Agent:
    """Villagers have different jobs around the village."""

    def reset(self, seed: int, observation: ThreeBranchesObservation) -> None:
        """Prepare for a day."""

        # Find this villager's number.
        player_id = me.player_id(observation)
        number = int(player_id.split("_")[1])

        # Give each villager a different role.
        if number == 1:
            self.role = "pump"
        elif number == 2:
            self.role = "bench1"
        elif number == 3:
            self.role = "bench2"
        elif number == 4:
            self.role = "crop1"
        elif number == 5:
            self.role = "crop2"
        elif number == 6:
            self.role = "crate1"
        elif number == 7:
            self.role = "crate2"
        elif number == 8:
            self.role = "wander1"
        elif number == 9:
            self.role = "wander2"
        else:
            self.role = "home"

        # Find the home doorway.
        home = me.home(observation)

        if home != "none":
            self.door = layout.doorway(observation, home)
        else:
            self.door = None

        # Remember the village props.
        self.pump = None
        self.benches = []
        self.crops = []
        self.crates = []

        for prop in props.all(observation):
            if prop["type"] == "pump":
                self.pump = _cell_centre(prop["cell"])

            if prop["type"] == "bench":
                self.benches.append(_cell_centre(prop["cell"]))

            if "crop" in prop["type"]:
                self.crops.append(_cell_centre(prop["cell"]))

            if "crate" in prop["type"]:
                self.crates.append(_cell_centre(prop["cell"]))

        # Route information.
        self.route = []
        self.route_index = 0
        self.route_target = None

        # Build the first route.
        self._make_route(observation)

    def _find_target(self, observation):
        """Find this villager's target."""

        target = None

        if self.role == "pump":
            target = self.pump

        elif self.role == "bench1":
            if len(self.benches) > 0:
                target = self.benches[0]

        elif self.role == "bench2":
            if len(self.benches) > 1:
                target = self.benches[1]

        elif self.role == "crop1":
            if len(self.crops) > 0:
                target = self.crops[0]

        elif self.role == "crop2":
            if len(self.crops) > 1:
                target = self.crops[1]
            elif len(self.crops) > 0:
                target = self.crops[0]

        elif self.role == "crate1":
            if len(self.crates) > 0:
                target = self.crates[0]

        elif self.role == "crate2":
            if len(self.crates) > 1:
                target = self.crates[1]
            elif len(self.crates) > 0:
                target = self.crates[0]

        elif self.role == "wander1":
            if len(self.crops) > 0:
                target = self.crops[0]
            elif self.pump is not None:
                target = self.pump

        elif self.role == "wander2":
            if len(self.crates) > 0:
                target = self.crates[0]
            elif self.pump is not None:
                target = self.pump

        elif self.role == "home":
            target = self.door

        return target

    def _find_reachable_target(
        self,
        observation: ThreeBranchesObservation,
        target
    ):
        """Find the closest walkable cell that can be reached."""

        start = layout.cell_at(
            observation,
            me.position(observation)
        )

        if start is None:
            return None

        frame = layout.frame(observation)
        cells_x = int(frame["cells_x"])
        cells_y = int(frame["cells_y"])

        queue = [start]
        visited = set()
        visited.add((start["x"], start["y"]))

        reachable_cells = []

        for current in queue:
            reachable_cells.append(current)

            neighbors = []

            neighbors.append({
                "x": current["x"] + 1,
                "y": current["y"]
            })

            neighbors.append({
                "x": current["x"] - 1,
                "y": current["y"]
            })

            neighbors.append({
                "x": current["x"],
                "y": current["y"] + 1
            })

            neighbors.append({
                "x": current["x"],
                "y": current["y"] - 1
            })

            for neighbor in neighbors:
                x = neighbor["x"]
                y = neighbor["y"]

                inside = (
                    x >= 0
                    and x < cells_x
                    and y >= 0
                    and y < cells_y
                )

                key = (x, y)

                if inside and key not in visited:
                    if layout.can_step(
                        observation,
                        current,
                        neighbor
                    ):
                        visited.add(key)
                        queue.append(neighbor)

        best_cell = None
        best_distance = None

        for cell in reachable_cells:
            centre = _cell_centre(cell)
            distance = geometry.distance(
                centre,
                target
            )

            if best_distance is None:
                best_distance = distance
                best_cell = cell
            elif distance < best_distance:
                best_distance = distance
                best_cell = cell

        return best_cell

    def _make_route(self, observation: ThreeBranchesObservation) -> None:
        """Build a route from the current cell to a safe target cell."""

        target = self._find_target(observation)

        if target is None:
            self.route = []
            self.route_index = 0
            self.route_target = None
            return

        start = layout.cell_at(
            observation,
            me.position(observation)
        )

        if start is None:
            self.route = []
            self.route_index = 0
            self.route_target = None
            return

        target_cell = self._find_reachable_target(
            observation,
            target
        )

        if target_cell is None:
            self.route = []
            self.route_index = 0
            self.route_target = None
            return

        frame = layout.frame(observation)
        cells_x = int(frame["cells_x"])
        cells_y = int(frame["cells_y"])
        max_cells = cells_x * cells_y

        queue = [start]
        visited = set()
        visited.add((start["x"], start["y"]))

        previous = {}

        for current in queue:
            neighbors = []

            neighbors.append({
                "x": current["x"] + 1,
                "y": current["y"]
            })

            neighbors.append({
                "x": current["x"] - 1,
                "y": current["y"]
            })

            neighbors.append({
                "x": current["x"],
                "y": current["y"] + 1
            })

            neighbors.append({
                "x": current["x"],
                "y": current["y"] - 1
            })

            for neighbor in neighbors:
                key = (
                    neighbor["x"],
                    neighbor["y"]
                )

                if key not in visited:
                    if layout.can_step(
                        observation,
                        current,
                        neighbor
                    ):
                        visited.add(key)
                        previous[key] = current
                        queue.append(neighbor)

        # Build the route backward from the target.
        route = []
        current = target_cell
        found_start = False

        for _ in range(max_cells):
            route.insert(0, current)

            # Stop when the route reaches the starting cell.
            if (
                current["x"] == start["x"]
                and current["y"] == start["y"]
            ):
                found_start = True
                break

            key = (
                current["x"],
                current["y"]
            )

            # Stop if the previous cell cannot be found.
            if key in previous:
                current = previous[key]
            else:
                break

        if found_start:
            self.route = route
            self.route_index = 0
            self.route_target = target
        else:
            self.route = []
            self.route_index = 0
            self.route_target = None

    def _route_needs_rebuild(self, observation) -> bool:
        """Check whether the current route should be rebuilt."""

        target = self._find_target(observation)

        if target is None:
            return False

        if self.route_target is None:
            return True

        if geometry.distance(
            target,
            self.route_target
        ) > 0.1:
            return True

        if self.route_index >= len(self.route):
            return True

        return False

    def _next_route_position(self, observation):
        """Return the next safe position on the current route."""

        current_cell = layout.cell_at(
            observation,
            me.position(observation)
        )

        if current_cell is None:
            return None

        # Remove route cells that the villager has already reached.
        while self.route_index < len(self.route):
            route_cell = self.route[self.route_index]

            if (
                current_cell["x"] == route_cell["x"]
                and current_cell["y"] == route_cell["y"]
            ):
                self.route_index += 1
            else:
                break

        if self.route_index >= len(self.route):
            return None

        next_cell = self.route[self.route_index]

        if layout.can_step(
            observation,
            current_cell,
            next_cell
        ):
            return _cell_centre(next_cell)

        return None

    def act(
        self,
        observation: ThreeBranchesObservation
    ) -> ThreeBranchesAction:
        """Choose one simple order from the current observation."""

        heading = me.heading(observation)

        # Wave when somebody is visible.
        expression = "wave" if people.seen(observation) else "none"

        # Use a nearby bench.
        usable = props.usable(observation)

        if usable is not None and usable["type"] == "bench":
            if self.role == "bench1" or self.role == "bench2":
                return action.stand(
                    heading,
                    "use"
                )

        here = me.position(observation)

        # Rebuild the route only when necessary.
        if self._route_needs_rebuild(observation):
            self._make_route(observation)

        # Get the next position on the route.
        next_position = self._next_route_position(
            observation
        )

        if next_position is not None:
            # Keep walking without resetting the route after a brief pause.
            return action.walk(
                geometry.heading_to(
                    here,
                    next_position
                ),
                1.2,
                expression
            )

        # We have reached the safe target area.
        target = self._find_target(observation)

        if target is not None:
            return action.stand(
                geometry.heading_to(
                    here,
                    target
                ),
                expression
            )

        # Stop if there is no target.
        return action.stand(
            heading,
            expression
        )


# Optional: messaging. On your turn, chat receives messages addressed to
# your player since its previous turn. Return messages with a recipient
# and text, or nothing to stay silent. Use None as the recipient to broadcast.
# Every message is recorded and shown in replays.
#
# def chat(self, inbox: list[dict]) -> list[dict] | None:
#     ...
