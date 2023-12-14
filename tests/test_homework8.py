from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, pairing, final_exponentiate
import numpy as np
import random
import galois
from functools import reduce

def r1cs_to_qap(p, x, y, GF):
    # out = x^4 -5y^2x^2
    # v1 = x * x
    # v2 = v1 * v1         # x^4
    # v3 = -5y * y
    # -v2 + out = v3*v1
    # 1, out, x, y, v1, v2, v3
    L = np.array([
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, -5, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1],
    ])

    R = np.array([
        [0, 0, 1, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0],
    ])

    O = np.array([
        [0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1],
        [0, 1, 0, 0, 0, -1, 0],
    ])

    # x = 4
    # y = -2
    v1 = x * x
    v2 = v1 * v1         # x^4
    v3 = -5*y * y
    out = v3*v1 + v2    # -5y^2 * x^2

    witness = np.array([1, out, x, y, v1, v2, v3])

    assert all(np.equal(np.matmul(L, witness) * np.matmul(R, witness), np.matmul(O, witness))), "not equal"

    L_galois = GF(np.mod(L, p))
    R_galois = GF(np.mod(R, p))
    O_galois = GF(np.mod(O, p))
    
    # Correct witness
    # NOTE, the mod here might be wrong
    x = GF(x)
    y = GF(y % p) # we are using 79 as the field size, so 79 - 2 is -2
    v1 = x * x
    v2 = v1 * v1         # x^4
    v3 = GF(-5 % p)*y * y
    out = v3*v1 + v2    # -5y^2 * x^2

    witness = GF(np.array([1, out, x, y, v1, v2, v3]))

    assert all(np.equal(np.matmul(L_galois, witness) * np.matmul(R_galois, witness), np.matmul(O_galois, witness))), "not equal"

    def interpolate_column(col):
        xs = GF(np.array([1,2,3,4]))
        return galois.lagrange_poly(xs, col)

    # axis 0 is the columns. apply_along_axis is the same as doing a for loop over the columns and collecting the results in an array
    U_polys = np.apply_along_axis(interpolate_column, 0, L_galois)
    V_polys = np.apply_along_axis(interpolate_column, 0, R_galois)
    W_polys = np.apply_along_axis(interpolate_column, 0, O_galois)

    def inner_product_polynomials_with_witness(polys, witness):
        mul_ = lambda x, y: x * y
        sum_ = lambda x, y: x + y
        return reduce(sum_, map(mul_, polys, witness))

    Ua = inner_product_polynomials_with_witness(U_polys, witness)
    Va = inner_product_polynomials_with_witness(V_polys, witness)
    Wa = inner_product_polynomials_with_witness(W_polys, witness)

    # t = (x - 1)(x - 2)(x - 3)(x - 4)
    t = galois.Poly([1, p - 1], field = GF) * galois.Poly([1, p - 2], field = GF) * galois.Poly([1, p - 3], field = GF) * galois.Poly([1, p - 4], field = GF)
    
    h = (Ua * Va - Wa) // t

    assert Ua * Va == Wa + h * t, "division has a remainder"

    return (Ua, Va, Wa, h, t)

def fq_to_point(fq):
    return [repr(fq[0]), repr(fq[1])]

def fq2_to_point(fq):
    return [[repr(fq[0].coeffs[0]), repr(fq[0].coeffs[1])], [repr(fq[1].coeffs[0]), repr(fq[1].coeffs[1])]]

def easy_as_abc():
    GF = galois.GF(curve_order)
    # Randomise tau, alpha and beta
    tau = GF(random.randint(1, curve_order - 1))
    alpha = GF(random.randint(1, curve_order - 1))
    beta = GF(random.randint(1, curve_order - 1))
    
    # Our inputs
    x = random.randint(1,1000)
    y = random.randint(1,1000)
    
    # Generate QAP
    Ua, Va, Wa, h, t = r1cs_to_qap(curve_order, x, y, GF)
    
    # Calculate powers of tau for A and B and the random shift for A and B
    powers_of_tau_for_A = [multiply(G1,int(tau**i)) for i in range(Ua.degree + 1)]
    powers_of_tau_for_B = [multiply(G2,int(tau**i)) for i in range(Ua.degree + 1)]
    alpha1 = multiply(G1, int(alpha))
    beta2 = multiply(G2, int(beta))
    powers_of_tau_for_h_t = [multiply(G1, int(tau**i * t(tau))) for i in range(t.degree)]
    
    # Calculate A1 and B2
    A1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_A, Ua.coeffs[::-1])), None)
    A1 = add(alpha1, A1)
    B2 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_B, Va.coeffs[::-1])), None)
    B2 = add(beta2, B2)

    C_prime_1 = reduce(add, \
                  (multiply(point, int(int(beta)*int(ui) + int(alpha)*int(vi) + int(wi))) \
                    for point, ui, vi, wi in zip(powers_of_tau_for_A, Ua.coeffs[::-1], Va.coeffs[::-1], Wa.coeffs[::-1])), None)
    
    HT1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_h_t, h.coeffs[::-1])), None)
    C1 = add(C_prime_1, HT1)

    return A1, B2, C1, alpha1, beta2

def test_week_8_abc(homework8_contract):
    
    A1, B2, C1, alpha1, beta2 = easy_as_abc()

    assert final_exponentiate(pairing(B2, A1)) == final_exponentiate(pairing(beta2, alpha1) * pairing(G2, C1)), "sorry nope"

    # Onchain
    assert homework8_contract.verify_witness(fq_to_point(A1), fq2_to_point(B2), \
                                            fq_to_point(C1), fq_to_point(alpha1), \
                                            fq2_to_point(beta2))

if __name__ == "__main__":
    A1, B2, C1, alpha1, beta2 = easy_as_abc()

    assert final_exponentiate(pairing(B2, A1)) == final_exponentiate(pairing(beta2, alpha1) * pairing(G2, C1)), "sorry nope"