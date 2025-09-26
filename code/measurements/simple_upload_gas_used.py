from __future__ import annotations

import json

from dataclasses import dataclass
import matplotlib.pyplot as plt
from pathlib import Path
from pprint import pformat
from typing import Any, Literal

from shared.python.utils.metrics import MetricType

from shared_gas_used import (
    assert_field,
    combine_client_and_dpcn_data,
    DATA_ALGO_2_CLIENT_FOLDER,
    DATA_ALGO_3_CLIENT_FOLDER,
    DATA_DPCN_FOLDER,
)


def load_user_upload_data(algo: Literal["algo_2", "algo_3"]) -> dict[str, int]:
    file: Path
    id_name: Literal["request_id", "file_id"]
    if algo == "algo_2":
        file = DATA_ALGO_2_CLIENT_FOLDER / MetricType.A2_CLIENT_FILE_UPLOAD.get_file_name()
        id_name = "request_id"
    else:
        file = DATA_ALGO_3_CLIENT_FOLDER / MetricType.A3_CLIENT_FILE_UPLOAD.get_file_name()
        id_name = "file_id"

    data_raw: list[dict[str, str | int]]
    with file.open("r") as f:
        data_raw = json.load(f)

    ret: dict[str, int] = {}
    for data_point in data_raw:
        gas_used: int = assert_field(data_point, "gas_used", int)
        uid: int = assert_field(data_point, id_name, int)
        user: str = assert_field(data_point, "user", str)
        ret[f"{user}|{uid}"] = gas_used

    return ret


def load_dpcn_upload_data(algo: Literal["algo_2", "algo_3"]) -> dict[str, int]:
    gas_used_override: int | None = None
    file: Path
    id_name: Literal["request_id", "file_id"]
    if algo == "algo_2":
        file = DATA_DPCN_FOLDER / MetricType.A2_DPCN_SERVICED_REQUESTS.get_file_name()
        id_name = "request_id"
    else:
        file = DATA_ALGO_3_CLIENT_FOLDER / MetricType.A3_CLIENT_FILE_UPLOAD.get_file_name()
        gas_used_override = 0
        id_name = "file_id"

    data_raw: list[dict[str, str | int]]
    with file.open("r") as f:
        data_raw = json.load(f)

    ret: dict[str, int] = {}
    for data_point in data_raw:
        gas_used: int = assert_field(data_point, "gas_used", int)
        uid: int = assert_field(data_point, id_name, int)
        user: str = assert_field(data_point, "user", str)
        if gas_used_override is None:
            ret[f"{user}|{uid}"] = gas_used
        else:
            ret[f"{user}|{uid}"] = gas_used_override

    return ret


def load_upload_data(algo: Literal["algo_2", "algo_3"]) -> tuple[dict[str, int], dict[str, int]]:
    client_upload_data: dict[str, int] = load_user_upload_data(algo)
    dpcn_upload_data: dict[str, int] = load_dpcn_upload_data(algo)

    return (client_upload_data, dpcn_upload_data)

def load_merged_upload_data(algo: Literal["algo_2", "algo_3"]) -> list[int]:
    client_upload_data: dict[str, int]
    dpcn_upload_data: dict[str, int]

    client_upload_data, dpcn_upload_data = load_upload_data(algo)

    return combine_client_and_dpcn_data(
        client_data=client_upload_data,
        dpcn_data=dpcn_upload_data
    )
