import datetime

"""
Miscellaneous functions
"""


def gen_instruction_metadata():
    content = ""
    content += f"Navigation report (generated with Warehouse Navigator at {datetime.datetime.now().replace(microsecond=0)})\n"
    content += "=" * len(content)
    content += "\n"

    return content


def save_to_file(filename, str_lines: list[str]):
    with open(file=filename, mode="w") as f:
        f.writelines(str_lines)
