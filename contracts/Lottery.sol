// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;
    // OPENED - 0, CLOSED - 1, CALCULATING_WINNER - 2
    enum LOTTERY_STATE {
        OPENED,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;
    uint256 public fee;
    bytes32 public keyHash;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        address _link,
        uint256 _fee,
        bytes32 _keyHash
    ) VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATE.OPENED);
        require(
            msg.value >= getEntranceFee(),
            "Not enough ETH! Players need to enter with at least $50 worth of ether"
        );
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = ethUsdPriceFeed.latestRoundData();
        // 18 decimals = 8 (price decimals) + 10 (added, so that sum has 18)
        uint256 adjustedPrice = uint256(price) * 10**10;
        // This way usdEntryFee has 18 decimals and it has an additional 18 decimals that will be cancel after dividing
        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LOTTERY_STATE.CLOSED,
            "Can't start a new lottery yet!"
        );
        lotteryState = LOTTERY_STATE.OPENED;
    }

    function endLottery() public onlyOwner {
        lotteryState = LOTRETY_STATE.CALCULATING_WINNER;
        bytes32 requestId = requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 _requestId, uin256 _randomness)
        internal
        override
    {
        require(
            lotteryState == LOTTERY_STATE.CALCULATING_WINNER,
            "You aren't there yet!"
        );
        require(_randomness > 0, "Random not found");
    }
}
