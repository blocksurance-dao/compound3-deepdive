# compound3-deepdive
A deep dive into the Compound Protocol

As part of ongoing research into DeFi Lending, I recently made a deep dive into the CompoundIII (Comet) Protocol. This protocols is an open source protocol maintained by the Compound DAO. (https://github.com/compound-finance/comet)

The goal of the deep dive was to test the mathematical core. Several steps were taken to achieve this:

1) The Comet contracts were mined using the CometMiner.py included with this repository, and the data stored in MongoDB. The miner targeted the Supply event, and obtained additional data following these schema:

supply collection
{
    "from" : "0x4091243E3fB5E637D06c265C6EAe1Be7fb8460Ce",
    "dst" : "0x4091243E3fB5E637D06c265C6EAe1Be7fb8460Ce",
    "amount" : 25776.4195,
    "block" : 17828028,
    "repay" : true,
    "utilization" : 0.9990441160513406,
    "borrowRate" : 0.2202023521,
    "supplyRate" : 0.2206162105,
    "totalSupply" : 390462694.425454,
    "totalBorrow" : 390089450.758417,
    "reserves" : 1334336.549036
}

slopeRates collection
{
    "block" : 18896476,
    "utilization" : 0.9785596249484667,
    "borrowBaseRate" : 0.0317097919,
    "borrowSlopeLow" : 0.1055936073,
    "borrowSlopeHigh" : 4.7564687975,
    "supplyBaseRate" : 0.0,
    "supplySlopeLow" : 0.1078132927,
    "supplySlopeHigh" : 4.7564687975,
    "supplyKink" : 0.93,
    "borrowKink" : 0.93
}

2) Additional calculations were made to determine the theoretical breakeven rates based on the recorded supplyRate and utilization Calculate.ipynb, adding additional fields to the supply collection. (brekevenRate, works) The purpose was to determine whether the borrowRate used on every event block is in fact above the theoretical breakeven rate for the supplyRate and utilization. If it was, then the formula works, and was marked accordingly.

supply collection
{
    "from" : "0x4091243E3fB5E637D06c265C6EAe1Be7fb8460Ce",
    "dst" : "0x4091243E3fB5E637D06c265C6EAe1Be7fb8460Ce",
    "amount" : 25776.4195,
    "block" : 17828028,
    "repay" : true,
    "utilization" : 0.9990441160513406,
    "borrowRate" : 0.2202023521,
    "supplyRate" : 0.2206162105,
    "totalSupply" : 390462694.425454,
    "totalBorrow" : 390089450.758417,
    "reserves" : 1334336.549036,
    "breakevenRate" : 0.22082729576744994,
    "works" : false
}

3) This data is now shared via MongoDB Atlas, in case you don't want to spend the time mining the Compound Finance smart contracts. Fire up Visualize.ipynb and make queries this way. Also, the mongodump of the database is included with this repo. In case you want to mongorestore locally.


SUMMARY:
The key driver of the Compound Protocol is the utilization variable, which is derived based on the ration of the totalSupply and the totalBorrow. 

utilization = totalBorrow/totalSupply

Slope rates are used in conjunction with the utilization figures to determine what the borrow and supply rates should be at the time. Slope rates are left for manual adjustment by the DAO. Because the nature of the lending market is dynamic, the data shows that those rates are not adjusted fast or accurately enough, which causes about 10% of the transactions to show the borrow rate which is lower than the theoretical breakeven rate for the current utilization and supplyRate.

When this occurs, the protocol is bleeding chips from the reserve.

Furthermore, the protocol does not have a safeguard from utilization getting above 100%. 
As I mentioned earlier, utilization = totalBorrow/totalSupply. The protocol also features a reserve. What that does is create a situation where the totalBorrow can in fact become greater than the totalSupply, pushing the utilization rate above 100%. The getSupplyRate and getBorrowRate functions however are not equipped to handle this scenario producing theoretically incorrect reading on the rates. 
