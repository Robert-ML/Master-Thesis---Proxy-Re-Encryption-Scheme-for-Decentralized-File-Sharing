from __future__ import annotations

import json

from dataclasses import dataclass
from pathlib import Path
from pprint import pformat
from typing import Any, Literal

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

from shared.python.utils.metrics import MetricType


CHUNKS: int = 5


DATA_ALGO_2_CLIENT_FOLDER: Path = Path("./data/algo2_client/")
DATA_ALGO_3_CLIENT_FOLDER: Path = Path("./data/algo3_client/")
DATA_DPCN_FOLDER: Path = Path("./data/dpcn/")


def assert_field[T](dict: dict[str, Any], field: str, type: type[T]) -> T:
    assert isinstance(dict[field], type), f"Field of not the expected type {type}"
    return dict[field]


def indexes(length: int) -> list[int]:
    return list(range(1, length + 1))

def indexes_chunked(length: int, chunks: int) -> list[int]:
    return list(range(1, length // chunks + 1))

def values_chunked(data: list[int], chunks: int) -> list[int]:
    chunk_size: int = len(data) // chunks

    chunked_data: list[int] = []
    for i in range(chunk_size):
        s: int = 0
        for j in range(chunks):
            s += data[j * chunks + i]
        chunked_data.append(s // chunks)

    return chunked_data


def load_client_share_data(file: Path) -> dict[str, int]:
    data_raw: list[dict[str, str | int]]
    with file.open("r") as f:
        data_raw = json.load(f)

    ret: dict[str, int] = {}
    for data_point in data_raw:
        gas_used: int = assert_field(data_point, "gas_used", int)
        request_id: str = assert_field(data_point, "request_id", str)
        user: str = assert_field(data_point, "user", str)
        ret[f"{user}|{request_id.split("|")[1]}"] = gas_used

    return ret


def load_dpcn_share_data(file: Path) -> dict[str, int]:
    data_raw: list[dict[str, str | int]]
    with file.open("r") as f:
        data_raw = json.load(f)

    ret: dict[str, int] = {}
    for data_point in data_raw:
        gas_used: int = assert_field(data_point, "gas_used", int)
        uid: int = assert_field(data_point, "file_no", int)
        user: str = assert_field(data_point, "client", str)
        ret[f"{user}|{uid}"] = gas_used

    return ret


def combine_client_and_dpcn_data(client_data: dict[str, int], dpcn_data: dict[str, int]) -> list[int]:
    ret: list[int] = []

    for key, gas_used in client_data.items():
        ret.append(gas_used + dpcn_data[key])

    return ret


def plot_data(client_share_data: dict[str, int], dpcn_share_data: dict[str, int]) -> None:
    # Plotting
    plt.figure(figsize=(10, 5))

    plt.plot(indexes_chunked(len(client_share_data), CHUNKS), values_chunked(list(client_share_data.values()), CHUNKS), marker='o', linestyle='-', color='blue', label='Gas Used by Client During Share Request')
    plt.plot(indexes_chunked(len(dpcn_share_data), CHUNKS), values_chunked(list(dpcn_share_data.values()), CHUNKS), marker='o', linestyle='-', color='red', label='Gas Used by DPCN During Share Request')


    # Add labels and title
    plt.xlabel('Files Shared')
    plt.ylabel('Gas Used')
    # plt.title('Gas Used vs Number of Files Uploaded (Showing Constancy)')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()



def load_share_data(algo: Literal["algo_2", "algo_3"]) -> tuple[dict[str, int], dict[str, int]]:
    client_share_data: dict[str, int]
    dpcn_share_data: dict[str, int]

    if algo == "algo_2":
        client_share_data = load_client_share_data(DATA_ALGO_2_CLIENT_FOLDER / MetricType.A2_CLIENT_SHARE_REQUEST.get_file_name())
        dpcn_share_data = load_dpcn_share_data(DATA_DPCN_FOLDER / MetricType.A2_DPCN_SHARE_REQUESTS.get_file_name())
    else:
        client_share_data: dict[str, int] = load_client_share_data(DATA_ALGO_3_CLIENT_FOLDER / MetricType.A3_CLIENT_SHARE_REQUEST.get_file_name())
        dpcn_share_data: dict[str, int] = load_dpcn_share_data(DATA_DPCN_FOLDER / MetricType.A3_DPCN_SHARE_REQUESTS.get_file_name())

    return (client_share_data, dpcn_share_data)


def load_merged_share_data(algo: Literal["algo_2", "algo_3"]) -> list[int]:
    client_share_data: dict[str, int]
    dpcn_share_data: dict[str, int]

    client_share_data, dpcn_share_data = load_share_data(algo)

    return combine_client_and_dpcn_data(client_share_data, dpcn_share_data)


def main():
    # load data
    a2_client_share_data: dict[str, int] = load_client_share_data(DATA_ALGO_2_CLIENT_FOLDER / MetricType.A2_CLIENT_SHARE_REQUEST.get_file_name())
    a2_dpcn_share_data: dict[str, int] = load_dpcn_share_data(DATA_DPCN_FOLDER / MetricType.A2_DPCN_SHARE_REQUESTS.get_file_name())
    a2_data: list[int] = combine_client_and_dpcn_data(a2_client_share_data, a2_dpcn_share_data)

    a3_client_share_data: dict[str, int] = load_client_share_data(DATA_ALGO_3_CLIENT_FOLDER / MetricType.A3_CLIENT_SHARE_REQUEST.get_file_name())
    a3_dpcn_share_data: dict[str, int] = load_dpcn_share_data(DATA_DPCN_FOLDER / MetricType.A3_DPCN_SHARE_REQUESTS.get_file_name())
    a3_data: list[int] = combine_client_and_dpcn_data(a3_client_share_data, a3_dpcn_share_data)

    # plot_data(
    #     client_share_data=a2_client_share_data,
    #     dpcn_share_data=a2_dpcn_share_data,
    # )

    plot_violin(
        a2_data=a2_data,
        a3_data=a3_data,
    )

if __name__ == "__main__":
    main()