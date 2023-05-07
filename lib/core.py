import csv
from math import floor
from collections import OrderedDict

""" Configuration Constants """
# Initializes the map with specific size
DEFAULT_ROWS = 21
DEFAULT_COLS = 40


class Config:
    def __init__(self, random_item=False) -> None:
        self.random_item = random_item
        self.worker_position = (0, 0)


""" Data processing """


# Read data from the file
def read_inventory_data(file_path: str):
    id = []
    col = []
    row = []

    # Read data
    with open(file_path) as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for row in reader:
            id.append(row[0])
            col.append(row[1])
            row.append(row[2])

    id, col, row = id[1:], col[1:], row[1:]  # Remove the table header
    col = [floor(float(a)) for a in col]  # Drop the decimals in xLocation
    row = [int(b) for b in row]

    # Product database
    prod_db = OrderedDict()

    # Initialize an empty map
    # Note: 0 - empty, 1 - shelf
    # Column - X, Row - Y
    cols, rows = DEFAULT_COLS, DEFAULT_ROWS
    map_data = [[0] * cols for r in rows]

    for i, r, c in zip(id, row, col):
        prod_db[i] = (r, c)  # TODO: Replace with a Prod class
        # Set all shelves to 1
        map_data[r][c] = 1

    return map_data, prod_db
