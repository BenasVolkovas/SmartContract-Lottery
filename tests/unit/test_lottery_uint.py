from brownie import Lottery, accounts, network, config, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
from web3 import Web3
import pytest


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    lottery = deploy_lottery()
    # Act
    # 2000 usd  - 1 eth
    # 50 usd    - x eth
    # x = 0.025
    entranceFee = lottery.getEntranceFee()
    expectedEntranceFee = Web3.toWei(0.025, "ether")
    # Assert
    assert entranceFee == expectedEntranceFee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entranceFee = lottery.getEntranceFee()
    # Act & Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": entranceFee})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entranceFee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": entranceFee})
    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entranceFee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": entranceFee})
    # Act
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # Assert
    assert lottery.lotteryState() == 2


def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entranceFee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": entranceFee})
    lottery.enter({"from": get_account(index=1), "value": entranceFee})
    lottery.enter({"from": get_account(index=2), "value": entranceFee})
    fund_with_link(lottery)
    STATIC_RNG = 771
    startingBalanceOfAccount = account.balance()
    balanceOfLottery = lottery.balance()
    # Act
    tx = lottery.endLottery({"from": account})
    requestId = tx.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, STATIC_RNG, lottery.address, {"from": account}
    )
    # 771 % 3 = 0

    # Assert
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == startingBalanceOfAccount + balanceOfLottery
