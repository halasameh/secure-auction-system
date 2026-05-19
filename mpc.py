# mpc.py - Secure multiparty computation on additive secret shares

def mpc_add(a_shares, b_shares, p):
    #adds the secret shares of a and the secret shares of b 
    #adds each a to its respective and does the mod than puts the result in a new list in additive secret sharing form 
    return [(a + b) % p for (a, b) in zip(a_shares, b_shares)] # (a1 + b1, a2 + b2, a3 + b3)


#does the same as mpc add but with subtraction 
def mpc_sub(a_shares, b_shares, p):

    return [(a - b) % p for (a, b) in zip(a_shares, b_shares)] #(a1 - b1, a2 - b2, a3 - b3)

#multiplication can't be done directly on the given shares
def mpc_mult(a_shares, b_shares, p): #reconstruction → multiply → re-share

    # Reconstruct a and b get the sum of a shares and the sum of b shares mod p then multiplying them all mod p
    a = sum(a_shares) % p
    b = sum(b_shares) % p
    c = (a * b) % p #multiply

    # Re-share c across 3 parties
    from secretsharing import share_value
    return share_value(c, p)

#compare the shared values of a and b 
def mpc_compare(a_shares, b_shares, p):

    # compute share-wise difference di = ai - bi mod p
    #subtract the shares
    diff_shares = [(a - b) % p for (a, b) in zip(a_shares, b_shares)]

    # reconstruct the difference delta a - b (mod p)
    delta = sum(diff_shares) % p

    # interpret delta in signed integer space
    if delta == 0:
        return 0 #if equal

    if delta > p//2:
        return -1 #b > a
    return 1 #a > b

#list of shared bids (3 parties)
def mpc_argmax(list_of_shared_bids, p): #find the index and the value of the max bid
  #start with the first value as max
    max_index = 0 #start with max index 0
    max_shares = list_of_shared_bids[0] # start with the first item in the shared bids as the largest item

    for i in range(1, len(list_of_shared_bids)): # loops on the list of shared bids 
        compare_result = mpc_compare(list_of_shared_bids[i], max_shares, p) #compares the result of the shared bids using the method compare
        if compare_result == 1:  # if the new value in the list is greater
            max_index = i # the index of the new item is updated a
            max_shares = list_of_shared_bids[i] # and maxes the max share the inner value of the item

    return max_index, max_shares # returns max index and max share
