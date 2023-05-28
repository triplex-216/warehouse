# Resolves class type hinting itself, see https://stackoverflow.com/a/33533514
from __future__ import annotations

import csv
from math import floor

""" Configuration Constants """
# Initializes the map with specific size
DEFAULT_ROWS = 21
DEFAULT_COLS = 40


class Config:
    def __init__(
        self,
        use_random_item=False,
        save_instructions=False,
        default_algorithm="b",  # branch and bound by default
        origin_position=(0, 0),
        end_position=(0, 0),
    ) -> None:
        self.use_random_item = use_random_item
        self.save_instructions = save_instructions
        self.default_algorithm = default_algorithm
        self.origin_position = origin_position
        self.end_position = end_position


""" Data processing """


class AccessPoint:
    def __init__(self, coord: tuple[int, int]) -> None:
        self.coord = coord
        self.dv = dict()  # Initialize distance vector

    def add_path(
        self, destination: AccessPoint, distance: int, path: list[tuple[int, int]]
    ) -> None:
        """
        Add a path to the distance vector. The path goes from this AP
        to another AP with a tuple containing the path's distance and
        grid-by-grid path to take
        """
        self.dv[destination] = (distance, path)

    def get_nearest_ap(self) -> tuple[int, list[tuple[int, int]]]:
        """
        Return the nearest AP stored in the current AP's distance vector
        """
        return min(self.dv.items(), key=lambda item: item[1][0])


class Prod:
    def __init__(self, id: int, coord: tuple[int, int], _map) -> None:
        self.id, self.coord = id, coord

        # The product's neighbors; initialized with empty elements and will be updated later
        self._neigh = {"n": None, "e": None, "s": None, "w": None}
        # Bind reference to the map from which this product instance was created
        self._map = _map

        # Detect valid neighbors (access points)
        neighbors = get_neighbors(self._map, self.coord)
        # Assign each neighbor to a direction (n/s/e/w)
        for n in neighbors:
            offset = (n[0] - self.coord[0], n[1] - self.coord[1])
            match offset:
                case (1, 0):
                    self._neigh["n"] = AccessPoint(coord=n)
                case (0, 1):
                    self._neigh["e"] = AccessPoint(coord=n)
                case (-1, 0):
                    self._neigh["s"] = AccessPoint(coord=n)
                case (0, -1):
                    self._neigh["w"] = AccessPoint(coord=n)

    @property
    def x(self) -> int:
        return self.coord[0]

    @property
    def y(self) -> int:
        return self.coord[1]

    @property
    def n(self) -> AccessPoint:
        return self._neigh["n"]

    @property
    def e(self) -> AccessPoint:
        return self._neigh["e"]

    @property
    def s(self) -> AccessPoint:
        return self._neigh["s"]

    @property
    def w(self) -> AccessPoint:
        return self._neigh["w"]

    @property
    def neighbors(self) -> list[AccessPoint]:
        return self._neigh


# Read data from the file
def read_inventory_data(file_path: str) -> tuple[list[list[int]], dict[Prod]]:
    """
    Input:
        file_path: Path to the inventory dataset file

    Output:
        map_data: A 2D list describing the warehouse map.
        prod_db: An dictionary; key is the product's id, and the value
                 is a Prod instance describing that product
    """
    id = []
    col = []
    row = []

    # Read data
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for curr in reader:  # For every data (row)
            id.append(curr[0])
            col.append(curr[1])
            row.append(curr[2])

    id, col, row = id[1:], col[1:], row[1:]  # Remove the table header
    id = [int(i) for i in id]
    col = [floor(float(a)) for a in col]  # Drop the decimals in xLocation
    row = [int(b) for b in row]

    # Product database
    prod_db = dict()

    # Initialize an empty map, it should be a 2-d list[40][21]
    # Note: 0 - empty, 1 - shelf
    # Column - X, Row - Y, map[X][Y]
    cols, rows = DEFAULT_COLS, DEFAULT_ROWS
    map_data = [[0] * rows for _ in range(cols)]

    for i, r, c in zip(id, row, col):
        # Set all shelves to 1
        map_data[c][r] = 1
        prod_db[i] = Prod(id=i, coord=(c, r), _map=map_data)

    return map_data, prod_db


def get_item(product_db: dict, id_list: list) -> list[Prod]:
    prod_list = []
    for id in id_list:
        try:
            prod_list.append(product_db[id])
        except KeyError:
            print(f"Item {id} not found, skipping...")

    return prod_list


def get_item_locations(product_db: dict, id_list: list) -> list[tuple[int, int]]:
    return [item.get_location() for item in get_item(product_db, id_list)]


def get_neighbors(map, node):
    neighbors = []
    dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    row, col = len(map), len(map[0])
    for d_x, d_y in dir:
        neighbor = (node[0] + d_x, node[1] + d_y)
        if (
            neighbor[0] in range(row)
            and neighbor[1] in range(col)
            and map[neighbor[0]][neighbor[1]] == 0
        ):
            neighbors.append(neighbor)

    return neighbors
