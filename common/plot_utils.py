"""Unified plot style so the report looks consistent."""
import matplotlib
matplotlib.use("Agg")  # save figures to files, no pop-up windows
import matplotlib.pyplot as plt


def setup_style():
    plt.rcParams.update({
        "figure.figsize": (10, 5),
        "axes.grid": False,   # use ax.grid(True) for signal plots
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "legend.fontsize": 10,
        "savefig.dpi": 150,
    })


def save_fig(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


setup_style()