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
    ) -> None:
        self.use_random_item = use_random_item
        self.save_instructions = save_instructions
        self.default_algorithm = default_algorithm
        self.origin_position = origin_position


""" Data processing """


class Prod:
    def __init__(self, id: int, x: int, y: int, _map) -> None:
        self.id, self.x, self.y = id, x, y

        # the product's neighbors; initialized with an empty list and will be updated after the first call of get_neighbors
        self._neigh = []
        # reference to the map from which this product instance was created
        self._map = _map

    def get_location(self):
        return (self.x, self.y)

    def neighbors(self):
        if not self._neigh:
            dir = [(1, 0), (-1, 0), (0, 1), (0, -1)]
            row, col = len(self._map), len(self._map[0])
            for d_x, d_y in dir:
                neighbor = (self.x + d_x, self.y + d_y)
                if (
                    neighbor[0] in range(row)
                    and neighbor[1] in range(col)
                    and self._map[neighbor[0]][neighbor[1]] == 0
                ):
                    self._neigh.append(neighbor)
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

    # Initialize an empty map
    # Note: 0 - empty, 1 - shelf
    # Column - X, Row - Y
    cols, rows = DEFAULT_COLS, DEFAULT_ROWS
    map_data = [[0] * cols for _ in range(rows)]

    for i, r, c in zip(id, row, col):
        # Set all shelves to 1
        map_data[r][c] = 1
        prod_db[i] = Prod(id=i, x=r, y=c, _map=map_data)

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
