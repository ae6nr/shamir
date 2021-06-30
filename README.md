# shamir

This is an example implementation of [Shamir's secret sharing algorithm](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing) on a finite field.

The secret (a number) can be divided between `n` shares so that given any `k` shares, the secret can be recovered.
However, *no* information about the secret can be inferred with less than `k` shares.

This works by generating a random polynomial of degree `k-1` that passes through the secret number at zero, and then choosing `n` other points on that polynomial.
Since a degree `k-1` polynomial is uniquely determined by `k` points, the polynomial may be reconstructed with `k` shares using [Lagrange polynomials](https://en.wikipedia.org/wiki/Lagrange_polynomial).
The reconstructed polynomial is evaluated at zero to recover the secret.

This process is a bit more complicated on a finite field due to finite field arithmetic, but the main ideas are the same.
