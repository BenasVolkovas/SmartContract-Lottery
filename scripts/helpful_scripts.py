from brownie import (
    network,
    accounts,
    config,
    Contract,
    interface,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
)

DECIMALS = 8
INITIAL_VALUE = 2000 * 10 ** 8

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

# Get account depending on active network chain
def get_account(index=None, id=None):
    if index:
        return accounts[index]

    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    # Default
    return accounts.add(config["wallets"]["from_key"])


contractToMock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


"""
This function will grab the contract addresses from the brownie config if defined,
otherwise, it will deploy a mock version of that contract, and
return that mock contract.

Args:
    contract_name (string)

Returns:
    brownie.network.contract.ProjectContract: The most recently deployed
    version of this contract.
"""


def get_contract(contract_name):
    # Get the type from the contract name
    contractType = contractToMock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # MockV3Aggregator.length <= 0
        if len(contractType) <= 0:
            # Deploy new mock if none is found
            deploy_mocks()

        # MockV3Aggregator[-1]
        contract = contractType[-1]

    else:
        # On real network, not development
        contractAddress = config["networks"][network.show_active()][contract_name]
        # MockV3Aggregator._name & MockV3Aggregator.abi
        contract = Contract.from_abi(
            contractType._name, contractAddress, contractType.abi
        )

    return contract


# Deploy needed mocks for local testing
def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    linkToken = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(linkToken.address, {"from": account})
    print("Mocks Deployed!")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=100000000000000000
):  # 0.1 LINK
    account = account if account else get_account()
    linkToken = link_token if link_token else get_contract("link_token")
    tx = linkToken.transfer(contract_address, amount, {"from": account})
    # linkTokenContract = interface.LinkTokenInterface(linkToken.address)
    # tx = linkTokenContract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Funded contract!")

    return tx
