// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal ethUsdPriceFeed;

    constructor(address _priceFeedAddress) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    }

    function enter() public payable {
        // $50 minimum
        players.push(payable(msg.sender));
    }

    function getEntrenceFee() public view returns (uint256) {
        (, int256 price, , , , ) = ethUsdPriceFeed.latestRoundData;
    }

    function startLottery() public {}

    function endLottery() public {}
}
