import asyncio
import logging
import secrets

from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from functools import partial
from hexbytes import HexBytes
from pprint import pformat
from typing import Coroutine
from typing_extensions import override

from eth_account.datastructures import SignedTransaction
from eth_typing import ChecksumAddress
from web3.types import Nonce, TxParams, TxReceipt
from shared.python.crypto.prenc.isshiki_2013 import to_int_array

from py_ecc.fields import (
    bn128_FQ12 as FQ12,
)

from core.common_vars import CommonVars
from core.file_credentials import FilePrencCredentials
from shared.python.crypto.prenc.encryptor import PrencEncryptor
from shared.python.crypto.prenc.isshiki_2013 import Isshiki_PrivateKey, Isshiki_PublicParameters, Isshiki_Cyphertext_LV2
from shared.python.crypto.utils import get_random_int
from shared.python.evm.force_transact import force_transaction
from shared.python.evm.connection import EvmConnection
from shared.python.utils.asynckit import create_task_log_on_fail
from shared.python.utils.metrics import Metric, MetricsCollector, MetricType


_LISTEN_PERIOD: timedelta = timedelta(seconds=5)
_DEFAULT_FILE_INFO: str = "Metadata"
_DEFAULT_FILE_ADDRESS: str = "youtu.be/dQw4w9WgXcQ"

_GasUsed = int


class FileUploader:
    def __init__(self, evm_connection: EvmConnection):
        self.__connection: EvmConnection = evm_connection

    @property
    def address(self) -> ChecksumAddress:
        return self.__connection.account.address


    async def generate_upload_file(self) -> int:
        file_id: int = get_random_int()

        logging.info(f"User \"{self.address}\" uploading file with id: {file_id}")

        # obtain the dpcn associated public key
        # Because this is not a transaction and all is simulated for this algo, it is not necessary to actually get it

        # upload the file
        gas_used: _GasUsed = await self.__upload_file(
            file_id=file_id,
            dpcn_accessible_sym_key=0,
        )

        logging.info(f"User \"{self.address}\" finished uploading file with id: {file_id} | gas used: {gas_used}")

        MetricsCollector.add(_MetricClientFileUpload(
            user=self.address,
            file_id=file_id,
            gas_used=gas_used,
        ))

        return file_id


    async def __upload_file(self, file_id: int, dpcn_accessible_sym_key: int) -> _GasUsed:
        proto_transaction = self.__connection.contract.functions.upload_file(
            owner=self.address,
            file_id=file_id,
            file_info=_DEFAULT_FILE_INFO,
            file_address=_DEFAULT_FILE_ADDRESS,
            owner_accessible_sym_key=0,
            dpcn_accessible_sym_key=dpcn_accessible_sym_key,
        )

        tx_hash: HexBytes = await force_transaction(proto_transaction, self.__connection)

        receipt: TxReceipt = await self.__connection.connection.eth.wait_for_transaction_receipt(tx_hash, timeout=300)

        # logging.info(f"Transaction receipt:\n" + pformat(receipt, sort_dicts=False))
        gas_used: int = int(receipt["gasUsed"])

        return gas_used


# ----------------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------------


class _MetricClientFileUpload(Metric):
    def __init__(self, user: str, file_id: int, gas_used: int) -> None:
        super().__init__(MetricType.A3_CLIENT_FILE_UPLOAD)
        self._user: str = user
        self._file_id: int = file_id
        self._gas_used: int = gas_used

    @override
    def get_dict(self) -> dict[str, int | float | str]:
        return {
            "user": self._user,
            "file_id": self._file_id,
            "gas_used": self._gas_used,
        }
