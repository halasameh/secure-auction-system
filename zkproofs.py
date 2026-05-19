# zkproofs.py - Simplified Zero-Knowledge Range Proofs (Fiat–Shamir style)
#bid is within the valid range without revealing it

import hashlib
#generate the range proof takes the value of the r and the bid and the limits of my range proof
def generate_range_proof(bid, randomness, lower_bound, upper_bound):
  #put all the parameters in a string seperated by |
    message = f"{bid}|{randomness}|{lower_bound}|{upper_bound}" #separated by | just to avoid confusion
    proof = hashlib.sha256(message.encode()).hexdigest() #hash the message and convert it in a hexadecimal format
    return proof #returning the zkp

#verifying the range proof with the same parameters as generating
def verify_range_proof(bid, randomness, proof, lower_bound, upper_bound):

    # the shamir proof checks if the bid is not within a valid range returns false
    if not (lower_bound <= bid <= upper_bound):
        return False #True if valid, False otherwise

    # if false is returned the verifier computes the expected message and the expected hash(supposed to have the same hash)
    expected_message = f"{bid}|{randomness}|{lower_bound}|{upper_bound}" #rebuild same msg
    expected_proof = hashlib.sha256(expected_message.encode()).hexdigest() #rebuild the same hash

    # compare with provided proof
    return expected_proof == proof #if the hashes are similar it return true if not it returns false 
