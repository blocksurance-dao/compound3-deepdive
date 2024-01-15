#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:24:27 2023

@author: alexei@blocksurance.io
"""
import json
from web3 import Web3
from pymongo.mongo_client import MongoClient

client = MongoClient("mongodb://localhost:27017/")

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Setup
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/<YourKeyHere>"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

with open('comet-abi.json') as user_file:
    file_contents = user_file.read()

parsed_json = json.loads(file_contents)

COMET_ADDRESS = "0xc3d688B66703497DAA19211EEdff47f25384cdc3"  # //mainnet
COMET_ABI = parsed_json['abi']


def main():
    contract = w3.eth.contract(address=COMET_ADDRESS, abi=COMET_ABI)
    # mines comet from deploy block to end of year 2023
    logs = contract.events.Supply().get_logs(fromBlock=15331587, toBlock=18829964)
    logs2 = contract.events.Supply().get_logs(fromBlock=18829965, toBlock=18908894)
    logs3 = logs + logs2

    db = client.compound
    collection = db.supply
    collection2 = db.slopeRates

    for log in logs3:
        # if log['blockNumber'] < 16007450: continue
        print(log['blockNumber'])
        utilization = contract.functions.getUtilization().call(
            block_identifier=log['blockNumber']-1)
        borrowRate = contract.functions.getBorrowRate(
            utilization).call(block_identifier=log['blockNumber']-1)
        supplyRate = contract.functions.getSupplyRate(
            utilization).call(block_identifier=log['blockNumber']-1)
        debt = contract.functions.borrowBalanceOf(
            log.args['dst']).call(block_identifier=log['blockNumber']-1)
        repay = debt > 0
        supply = contract.functions.totalSupply().call(
            block_identifier=log['blockNumber']-1)
        borrow = contract.functions.totalBorrow().call(
            block_identifier=log['blockNumber']-1)
        reserves = contract.functions.getReserves().call(
            block_identifier=log['blockNumber']-1)

        supplyKink = contract.functions.supplyKink().call(
            block_identifier=log['blockNumber']-1)
        borrowKink = contract.functions.borrowKink().call(
            block_identifier=log['blockNumber']-1)
        borrowBaseRate = contract.functions.borrowPerSecondInterestRateBase().call(
            block_identifier=log['blockNumber']-1)
        borrowSlopeLowRate = contract.functions.borrowPerSecondInterestRateSlopeLow().call(
            block_identifier=log['blockNumber']-1)
        borrowSlopeHighRate = contract.functions.borrowPerSecondInterestRateSlopeHigh().call(
            block_identifier=log['blockNumber']-1)
        supplyBaseRate = contract.functions.supplyPerSecondInterestRateBase().call(
            block_identifier=log['blockNumber']-1)
        supplySlopeLowRate = contract.functions.supplyPerSecondInterestRateSlopeLow().call(
            block_identifier=log['blockNumber']-1)
        supplySlopeHighRate = contract.functions.supplyPerSecondInterestRateSlopeHigh().call(
            block_identifier=log['blockNumber']-1)
        divisor = 10000000000
        decimals = 1000000

       # print(log.args['from'], log.args['dst'], log.args['amount'], log['blockNumber'])
        doc = {
            "from": log.args['from'],
            "dst": log.args['dst'],
            "amount": log.args['amount']/decimals,
            "block": log['blockNumber'],
            "repay": repay,
            "utilization": utilization/1000000000000000000,
            "borrowRate": borrowRate/divisor,
            "supplyRate": supplyRate/divisor,
            "totalSupply": supply/decimals,
            "totalBorrow": borrow/decimals,
            "reserves": reserves/decimals
        }
        collection.insert_one(doc)

        doc2 = {
            "block": log['blockNumber'],
            "utilization": utilization/1000000000000000000,
            "borrowBaseRate": borrowBaseRate/divisor,
            "borrowSlopeLow": borrowSlopeLowRate/divisor,
            "borrowSlopeHigh": borrowSlopeHighRate/divisor,
            "supplyBaseRate": supplyBaseRate/divisor,
            "supplySlopeLow": supplySlopeLowRate/divisor,
            "supplySlopeHigh": supplySlopeHighRate/divisor,
            "supplyKink": supplyKink/1000000000000000000,
            "borrowKink": borrowKink/1000000000000000000
        }
        collection2.insert_one(doc2)
        # break

    doc_count = collection.count_documents({})
    print(doc_count)


if __name__ == '__main__':
    main()
