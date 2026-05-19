# secretsharing.py - Additive 3-party secret sharing for MPC
#s1 + s2 + s3 = bid (mod p)
import secrets
#share_value function divides the secret into 3 shares 
def share_value(bid, p):
  #the first 2 shares are 2 random numbers below p 
    # Generate two random shares
    s1 = secrets.randbelow(p) #random s1
    s2 = secrets.randbelow(p) #random s2
    #the third share is computed from the s(bid) -s1-s2 and must be in the mod p 
    #s3 is computed such that the sum matches the bid (s1 + s2 + s3) mod p == bid
    s3 = (bid - s1 - s2) % p
#return the 3 secret shares 
    return (s1, s2, s3)

 #Reconstruct the bid from the shares
def reconstruct(shares, p):
    return sum(shares) % p #bid = (s1 + s2 + s3) mod p
