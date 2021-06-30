import numpy as np
from pyfinite import ffield


class Shamir:

    def __init__(self,p):
        # parameters
        self.F = ffield.FField(p) # finite field with 2**p elements
        self.stype = np.uint32 # self._calcType(p). I chose this because I haven't gotten p > 30 working.

    def _evalPoly(self,a,x):
        """
        Given a polynomial a on the finite field F at x where a contains the coefficients of a len(a)-1 degree polynomial.
        a[0] contains the coefficient of the highest degree term, and a[-1] is a constant.
        
        e.g.
        if a is (3,), a represents a[0] * x**2 + a[1] * x + a[2]
        This function evaluates this polynomial as ((a[0] + x) * a[1]) + x * a[2].
        This is called Horner's method, and it is used to reduce the number of multiplies.
        """
        y = a[0]
        for i in range(1,len(a)):
            y = self.F.Multiply(y, x)
            y = self.F.Add(y, a[i])
        return y

    def generateShares(self,secret,n,k):
        """
        Given a secret, produce n shares with a threshold k.
        A new random polynomial is generated each time this function is called.
        Returns a dictionary of shares with the input to the polynomial as the key and the output as the value.
        """
        # generate a random polynomial
        a = np.zeros((k,),dtype=self.stype)
        for i in range(0,k-1): # select random coefficients
            a[i] = self.F.GetRandomElement()
        a[k-1] = secret # secret is the last element

        # evaluate the polynomial at 1,2,...,n.
        D = {} # shares
        for i in range(0,n):
            D[i+1] = self._evalPoly(a,i+1)
        return D

    def calcSecret(self,D):
        """
        Given a dictionary of shares (input as key, output as value), calculate the secret.
        Returns the secret.
        """
        idxs = list(D.keys())
        k = len(idxs) # number of shares given

        # evaluate terms of Lagrange polynomial at zero
        # see https://en.wikipedia.org/wiki/Lagrange_polynomial
        for i in range(0,k):
            for j in range(0,k):
                if i == j:
                    pass
                else:
                    D[idxs[i]] = self.F.Divide(self.F.Multiply(D[idxs[i]],idxs[j]),self.F.Subtract(idxs[i],idxs[j]))
        
        # sum terms to recover secret
        y = D[idxs[0]]
        for i in range(1,k):
            y = self.F.Add(y,D[idxs[i]]) 
        return y


if __name__ == "__main__":

    # example usage
    n = 6 # number of shares
    k = 4 # threshold
    h = 30 # number of bits of entropy (I run into issues using more than thirty on my computer)
    s = Shamir(h) # h bits max entropy
    secret = 0x0c07fefe # the secret to share, make sure this is less than 2 ** h
    D = s.generateShares(secret,n,k) # the shares

    # recover secret only using k of the n shares 
    i = np.random.choice(np.arange(0,n)+1,size=(k,),replace=False) # the indexes of the shares to use to recover the secret
    g = {j:D[j] for j in i} # givens are randomly selected from the shares in D
    guess = s.calcSecret(g) # reconstruct the secret

    # show results
    if guess == secret:
        print(f"Success! The secret was {secret} and was recovered successfully from {g}.")
        if len(i) < k:
            print(f"You needed {k} shares, but you had {len(i)}. So you just got lucky in this case.")
        elif len(i) > k:
            print(f"You needed {k} shares, but you had {len(i)}. You had more information than necessary.")
    else:
        print(f"Fail. The secret was {secret}, but you guessed {guess} from {g}.")
        print(f"You needed {k} shares, but you had {len(i)}.")
        if len(i) >= k:
            print(f"Did you choose a secret with too many bits of entropy?")