from brownie import network, accounts, config, MockV3Aggregator, Contract

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


contractToMock = {"eth_usd_price_feed": MockV3Aggregator}


def get_contract(contract_name):
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

    # Get the type from the contract name
    contractType = contractToMock[contract_name]
    print("Contract type: ", contractType)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # MockV3Aggregator.length <= 0
        if len(contractType) <= 0:
            # Deploy new mock if none is found
            deploy_mocks()

        # MockV3Aggregator[-1]
        contract = contractType[-1]

    else:
        contractAddress = config["networks"][network.show_active()][contract_name]
        # MockV3Aggregator._name & MockV3Aggregator.abi
        contract = Contract.from_abi(
            contractType._name, contractAddress, contractType.abi
        )

    return contract


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    print("Mocks Deployed!")
