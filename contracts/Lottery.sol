// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
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

    constructor(address _priceFeedAddress) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
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
        // Pseudorandom number
        // !Research Chinlink VRF for getting random number!
        // uint256(
        //     keccak256(
        //         abi.encodePacked(
        //             (
        //                 nonce, // nonce is predictable (aka, transactions number)
        //                 msg.sender, // msg.sender is predictable
        //                 block.difficulty, // can actually be manipulated by the miners!
        //                 block.timestamp // timestamp is predictable
        //             )
        //         )
        //     )
        // ) % players.length;
    }
}
