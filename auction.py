# auction.py

from commitments import generate_commitment_params, commit_bid, verify_commitment
from zkproofs import generate_range_proof, verify_range_proof
from secretsharing import share_value, reconstruct
from mpc import mpc_argmax
import secrets

# Get shared params (p, G, H)
#C = b*g + r*p mod p 
PARAMS = generate_commitment_params() #get the parameters generated in the method (p , g , h)
P = PARAMS["p"] #takes the p 
#lower bound and upper bound generated for the zkp
LOWER_BOUND = 100 
UPPER_BOUND = 1000

class BidderRecord: #Stores everything about a bidder for the simulation.

    def __init__(self, bidder_id, bid, commitment, randomness, proof, shares):
        self.bidder_id = bidder_id
        self.bid = bid                # only present for simulation / verification
        self.commitment = commitment  # published commitment
        self.randomness = randomness  # secret random used in commitment
        self.proof = proof            # simulated range proof
        self.shares = shares          # tuple of 3 shares (s1,s2,s3)
        self.accepted = False         # initially false

#intializes the auction with lower and upper bounds, pedersen parameters , empty list of registered bids
class Auction:
    def __init__(self, lower=LOWER_BOUND, upper=UPPER_BOUND, params=PARAMS):
        self.lower = lower
        self.upper = upper
        self.params = params
        self.p = params["p"]
        self.G = params["G"]
        self.H = params["H"]
        self.registered = []  # list of BidderRecord

#assign an id to a bidder if there is no bidder
    def register_bidder(self, bid, bidder_id=None): #self= the auction object itself

        if bidder_id is None:
            bidder_id = secrets.token_hex(4)

#main workflow
        #creates pedersen commitment
        #Commit to the bid (Pedersen-style simulation) to hide the bid Computes C = b*G + r*H mod p
        commitment, randomness = commit_bid(bid, randomness=None, params=self.params) #return (commitment, r)
        #applying the zkp
        # to prove the bid is within the range (builds and hashes the msg)
        proof = generate_range_proof(bid, randomness, self.lower, self.upper)
        #giving the secret shares
        # bid into 3 shares (mod p)
        shares = share_value(bid, self.p)
        #storing everything related to the bidder record to be able to compare in the auction
        #  create record and store everything about the bidder (we don't accept/reject yet - verification happens in run_auction)
        rec = BidderRecord(bidder_id=bidder_id, bid=bid,
                           commitment=commitment, randomness=randomness,
                           proof=proof, shares=shares)
        self.registered.append(rec) #Store the record
        return rec
#run the auction 
    def run_auction(self, verbose=True):

        valid_records = []
        for rec in self.registered: #verifies the proof and the commitment and makes sure they are equal 
            proof_ok = verify_range_proof(rec.bid, rec.randomness, rec.proof, self.lower, self.upper) #range proof verification re-hashes the bid + randomness + bounds.
            comm_ok = verify_commitment(rec.bid, rec.randomness, rec.commitment, params=self.params) #recomputes C and matches it, always true if value not changed

            rec.accepted = (proof_ok and comm_ok) #only accepted bidders are kept 
            if rec.accepted:
                valid_records.append(rec)

        if len(valid_records) == 0: #tells there is no valid bidders 
            print("No valid bidders.")
            return None, None

        list_of_shared_bids = [list(rec.shares) for rec in valid_records] # extracts the 3 party shares from the valid records
        #finds the maxindex and maxshares 
        max_index, max_shares = mpc_argmax(list_of_shared_bids, self.p)
        winner_rec = valid_records[max_index] # the winner is the one with the max index 

        winning_bid = reconstruct(tuple(max_shares), self.p) #reconstruct the winning bid from shares 

        if verbose:
            winner_position = max_index + 1  # convert to 1-based index 
            print(f"Winner = {winner_position}, Winning Bid = {winning_bid}") 

        return winner_rec.bidder_id, winning_bid



#test
if __name__ == "__main__":
    # Create auction instance
    auction = Auction()

    # Example 1: Bidders = 150, 920, 600 -> Winner = 920
    print("Example 1:")
    auction.registered = []  # clear
    auction.register_bidder(80, bidder_id="B1")
    auction.register_bidder(888, bidder_id="B2")
    auction.register_bidder(788, bidder_id="B3")
    auction.run_auction()
    print("\n")

    # Example 2: Bidders = 350, 350, 100, 300 -> Winner = first 350
    print("Example 2:")
    auction.registered = []
    auction.register_bidder(350, bidder_id="B1")
    auction.register_bidder(350, bidder_id="B2")
    auction.register_bidder(100, bidder_id="B3")
    auction.register_bidder(389, bidder_id="B4")
    auction.run_auction()
    print("\n")

    # Example 3: Bidders = 10, 999, 300, 700, 2000 -> 10 and 2000 invalid -> Winner = 999
    print("Example 3:")
    auction.registered = []
    auction.register_bidder(10, bidder_id="B1")    # invalid (below lower)
    auction.register_bidder(999, bidder_id="B2")   # valid
    auction.register_bidder(300, bidder_id="B3")   # valid
    auction.register_bidder(700, bidder_id="B4")   # valid
    auction.register_bidder(2000, bidder_id="B5")  # invalid (above upper)
    auction.run_auction()