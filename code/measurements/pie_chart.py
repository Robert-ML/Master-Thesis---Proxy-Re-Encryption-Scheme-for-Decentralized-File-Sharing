import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly
import plotly.express as px

from shared_gas_used import load_share_data
from simple_upload_gas_used import load_upload_data
from violin_plots import FIGURES_FOLDER



def get_pie_percentages(sample_1: dict[str, int], sample_2: dict[str, int]) -> list[float, float]:
    sum_1: float = sum(sample_1.values())
    sum_2: float = sum(sample_2.values())

    total: float = sum_1 + sum_2

    percentage_1: float = sum_1 * 100 / total
    percentage_2: float = sum_2 * 100 / total

    return [percentage_1, percentage_2]


def main():
    a2_upload_client: dict[str, int]
    a2_upload_dpcn: dict[str, int]

    a3_upload_client: dict[str, int]
    a3_upload_dpcn: dict[str, int]

    a2_upload_client, a2_upload_dpcn = load_upload_data(algo="algo_2")
    a3_upload_client, a3_upload_dpcn = load_upload_data(algo="algo_3")


    a2_share_client: dict[str, int]
    a2_share_dpcn: dict[str, int]

    a3_share_client: dict[str, int]
    a3_share_dpcn: dict[str, int]

    a2_share_client, a2_share_dpcn = load_share_data(algo="algo_2")
    a3_share_client, a3_share_dpcn = load_share_data(algo="algo_3")


    # Create subplots: 1 row × 4 columns
    fig, axs = plt.subplots(1, 4, figsize=(20, 5))  # Wider figure for better spacing

    # Example data for each pie
    data: list[tuple[list[float], list[str], str]] = [
        (get_pie_percentages(a2_upload_client, a2_upload_dpcn), ["File Owner", "DPCN"], "System 2 - File Upload"),
        (get_pie_percentages(a2_share_client, a2_share_dpcn), ["Client", "DPCN"], "System 2 - File Share"),
        # (get_pie_percentages(a3_upload_client, a3_upload_dpcn), ["File Owner", "DPCN"], "System 3 - File Upload"),
        ([100], ["File Owner"], "System 3 - File Upload"),
        (get_pie_percentages(a3_share_client, a3_share_dpcn), ["Client", "DPCN"], "System 3 - File Share"),
    ]

    # Flatten the axs array for easy looping
    axs = axs.flatten()

    # Plot each pie chart
    for i in range(4):
        sizes, labels, title = data[i]
        axs[i].pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
        axs[i].axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        axs[i].set_title(title)

    plt.tight_layout()
    # plt.show()
    plt.savefig(FIGURES_FOLDER + "gas_usage_distribution_pie_chart.pdf")



if __name__ == "__main__":
    main()
