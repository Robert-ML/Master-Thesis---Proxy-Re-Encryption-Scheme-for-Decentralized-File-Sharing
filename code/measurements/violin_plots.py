import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
import plotly.express as px

from shared_gas_used import load_merged_share_data
from simple_upload_gas_used import load_merged_upload_data

FIGURES_FOLDER: str = "./shared/figures/"


def annotate_for_creating_df[T](data: list[T], column_1: str, column_2: str) -> list[tuple[str, str, T]]:
    ret: list[tuple[str, str, T]] = []

    for d in data:
        ret.append((column_1, column_2, d))

    return ret

def reduce_data_to_n(data: list[int], n: int=100) -> list[int]:
    data = np.array(data)
    bins = np.array_split(data, n)
    return np.array([b.mean() for b in bins]).tolist()


def plot_violin(df: pd.DataFrame) -> None:
    # normalize the data
    df["Normalized Gas Used"] = df.groupby(["System", "Action"])["Gas Used"].transform(
        lambda x: (x - x.mean()) / x.std()
    )
    fig = px.violin(df, y="Normalized Gas Used", x="Action", color="System", box=False,
        # title="Gas used normalized per action and system"
    )
    plotly.io.write_image(fig, FIGURES_FOLDER + "violin_gas_usage_distribution.pdf", format="pdf")
    # fig.show()


def plot_boxes(system2_upload: list[int], system3_upload: list[int], system2_share: list[int], system3_share: list[int]) -> None:
    # data = [system2_upload, system3_upload, system2_share, system3_share]
    # labels = ["System 2 Upload", "System 3 Upload", "System 2 Share", "System 3 Share"]

    # plt.boxplot(data, labels=labels)
    # plt.ylabel("Gas Used")

    # plt.tight_layout()
    # plt.show()

    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=False)

    # Grouped data
    data1 = [system2_upload, system2_share]
    data2 = [system3_upload, system3_share]

    axes[0].boxplot(data1, labels=["System 2 Upload", "System 2 Share"])
    axes[0].set_title("System 2")

    axes[1].boxplot(data2, labels=["System 3 Upload", "System 3 Share"])
    axes[1].set_title("System 3")

    plt.tight_layout()
    plt.show()


def plot_lines(system2_upload: list[int], system3_upload: list[int], system2_share: list[int], system3_share: list[int]) -> None:
    system2_upload = reduce_data_to_n(system2_upload)
    system3_upload = reduce_data_to_n(system3_upload)
    system2_share = reduce_data_to_n(system2_share)
    system3_share = reduce_data_to_n(system3_share)

    x = range(len(system2_upload))  # X-axis (indices or time)

    # Create subplots: 1 row, 2 columns
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), sharex=True)

    # --- Left subplot: High-magnitude data ---
    ax1.plot(x, system2_upload, marker="o", label="System 2 Upload")
    ax1.plot(x, system2_share, marker="o", label="System 2 Share")
    ax1.set_title("System 2 (Higher Gas Usage)")
    ax1.set_ylabel("Gas Used")
    ax1.legend()
    ax1.grid(True)

    # --- Right subplot: Low-magnitude data ---
    ax2.plot(x, system3_upload, marker="o", label="System 3 Upload")
    ax2.plot(x, system3_share, marker="o", label="System 3 Share")
    ax2.set_title("System 3 (Lower Gas Usage)")
    ax2.legend()
    ax2.grid(True)

    # Shared X-axis label
    fig.text(0.5, 0.005, "Number of 10 Chunked Requests", ha="center")

    plt.tight_layout()
    # plt.show()
    plt.savefig(FIGURES_FOLDER + "systems_gas_usage_vs_requests_no.pdf")


def main() -> None:
    # load data
    a2_upload_data: list[int] = load_merged_upload_data(algo="algo_2")
    a3_upload_data: list[int] = load_merged_upload_data(algo="algo_3")

    a2_share_data: list[int] = load_merged_share_data(algo="algo_2")
    a3_share_data: list[int] = load_merged_share_data(algo="algo_3")

    # prep the data and create df
    prepping_data: list[tuple[str, str, int]] = []
    prepping_data += annotate_for_creating_df(a2_upload_data, "System 2", "Upload")
    prepping_data += annotate_for_creating_df(a3_upload_data, "System 3", "Upload")
    prepping_data += annotate_for_creating_df(a2_share_data, "System 2", "Share")
    prepping_data += annotate_for_creating_df(a3_share_data, "System 3", "Share")

    df: pd.DataFrame =pd.DataFrame(prepping_data, columns=["System", "Action", "Gas Used"])

    # plot violin
    plot_violin(df)

    # plot boxes
    # plot_boxes(
    #     system2_upload=a2_upload_data,
    #     system3_upload=a3_upload_data,
    #     system2_share=a2_share_data,
    #     system3_share=a3_share_data,
    # )

    # plot lines
    plot_lines(
        system2_upload=a2_upload_data,
        system3_upload=a3_upload_data,
        system2_share=a2_share_data,
        system3_share=a3_share_data,
    )


if __name__ == "__main__":
    main()

