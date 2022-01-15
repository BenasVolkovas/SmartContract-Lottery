from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
)
import pytest
import time


def test_can_pick_winner():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    # Arrange
    account = get_account()
    lottery = deploy_lottery()
    entranceFee = lottery.getEntranceFee()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": entranceFee + 1000000000})  # 1 Gwei
    lottery.enter({"from": account, "value": entranceFee + 1000000000})  # 1 Gwei
    fund_with_link(lottery)
    # Act
    lottery.endLottery({"from": account})
    # Wait for 3 minutes
    time.sleep(300)

    # Assert
    # TODO: fix assertion errors
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
