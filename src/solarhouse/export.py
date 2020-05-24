import os

import matplotlib.pyplot as plt
import mpld3
import pandas as pd


def as_file(pd_data: pd.DataFrame, type_file: str = "csv", path: str = "output") -> None:
    """ Export results to file. """

    file_path = os.path.join(path, "data.%s" % type_file)
    with open(file_path, "w", newline="") as file:
        if type_file == "csv":
            file.write(pd_data.to_csv())
        else:
            file.write(pd_data.to_json(orient="split"))
            pass
    return file_path


def as_html(pd_data: pd.DataFrame, output_file_dir: str) -> None:
    """ Create HTML page with graphics. """
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot(pd_data)
    file_obj = os.path.join(output_file_dir, "plots.html")
    mpld3.save_html(fig, file_obj)
