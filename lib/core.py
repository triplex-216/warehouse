import csv
from math import floor

""" Configuration Constants """
# Initializes the map with specific size
DEFAULT_ROWS = 21
DEFAULT_COLS = 40


class Config:
    def __init__(self, random_item=False) -> None:
        self.random_item = random_item
        self.worker_position = (0, 0)


""" Data processing """


class Prod:
    def __init__(self, id: int, x: int, y: int) -> None:
        self.id, self.x, self.y = id, x, y

    def get_location(self):
        return (self.x, self.y)


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
    map_data = [[0] * cols for r in range(rows)]

    for i, r, c in zip(id, row, col):
        prod_db[i] = Prod(id=i, x=r, y=c)
        # Set all shelves to 1
        map_data[r][c] = 1

    return map_data, prod_db


def get_item_locations(product_db: dict, id_list: list) -> list[tuple[int, int]]:
    prod_list = []
    for id in id_list:
        prod_list.append((product_db[id].x, product_db[id].y))
    return prod_list
