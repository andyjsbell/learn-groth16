from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, pairing, final_exponentiate, FQ12
import numpy as np
import random
import galois
from functools import reduce
# curve_order = 79

def r1cs_to_qap(p, x, y, GF):
    # out = 3x^2y + 5xy - x - 2y + 3
    # v1 = x * y
    # out = 3xv1 + 5v1 - x - 2y + 3
    # out - 5v1 + x + 2y -3 = 3xv1

    # 1, out, x, y, v1
    L = np.array([
        [0, 0, 1, 0, 0],
        [0, 0, 3, 0, 0],
    ])

    R = np.array([
        [0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1],
    ])

    O = np.array([
        [0, 0, 0, 0, 1],
        [-3, 1, 1, 2, -5],
    ])

    v1 = x * y
    out = 3*x*v1 + 5*v1 - x - 2*y +3 

    witness = np.array([1, out, x, y, v1])
    assert all(np.equal(np.matmul(L, witness) * np.matmul(R, witness), np.matmul(O, witness))), "not equal"

    L_galois = GF(np.mod(L, p))
    R_galois = GF(np.mod(R, p))
    O_galois = GF(np.mod(O, p))
    
    v1 = GF(x * y)
    out = GF(3)*GF(x)*v1 + GF(5)*v1 + GF(-x%p) + GF(-2*y%p) + GF(3) 

    witness = GF(np.array([1, out, x, y, v1]))

    assert all(np.equal(np.matmul(L_galois, witness) * np.matmul(R_galois, witness), np.matmul(O_galois, witness))), "not equal"
    
    def interpolate_column(col):
        xs = GF(np.array([1,2]))
        return galois.lagrange_poly(xs, col)

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
    # t = (x - 1)(x - 2)
    t = galois.Poly([1, p - 1], field = GF) * \
        galois.Poly([1, p - 2], field = GF)
    
    h = (Ua * Va - Wa) // t

    assert Ua * Va == Wa + h * t, "division has a remainder"

    return (Ua, Va, Wa, h, t, witness, U_polys, V_polys, W_polys)

def fq_to_point(fq):
    return [repr(fq[0]), repr(fq[1])]

def fq2_to_point(fq):
    return [[repr(fq[0].coeffs[0]), repr(fq[0].coeffs[1])], [repr(fq[1].coeffs[0]), repr(fq[1].coeffs[1])]]

def kept_secret(GF):
    tau = GF(3)
    alpha = GF(6)
    beta = GF(9)
    gamma = GF(12)
    delta = GF(15)

    return tau, alpha, beta, gamma, delta

def trusted_setup(GF, t, Ua, U, V, W):
    
    tau, alpha, beta, gamma, delta = kept_secret(GF)

    # Calculate powers of tau
    powers_of_tau_for_A = [multiply(G1,int(tau**i)) for i in range(Ua.degree + 1)]
    powers_of_tau_for_B = [multiply(G2,int(tau**i)) for i in range(Ua.degree + 1)]
    powers_of_tau_for_h_t = [multiply(G1, int(tau**i * t(tau) * pow(int(delta), -1, curve_order))) for i in range(t.degree)]
    alpha1 = multiply(G1, int(alpha))
    beta1 = multiply(G1, int(beta))
    beta2 = multiply(G2, int(beta))
    delta1 = multiply(G1, int(delta))
    delta2 = multiply(G2, int(delta))
    gamma2 = multiply(G2, int(gamma))

    C_public = [multiply(
        G1, 
        int((beta * u(tau) + alpha * v(tau) + w(tau)) * pow(int(gamma), -1, curve_order)))
        for u, v, w in zip(U[:2], V[:2], W[:2])]
    
    C_private = [multiply(
        G1, 
        int((beta * u(tau) + alpha * v(tau) + w(tau)) * pow(int(delta), -1, curve_order)))
        for u, v, w in zip(U[2:], V[2:], W[2:])]
    
    return powers_of_tau_for_A, \
            powers_of_tau_for_B, \
            powers_of_tau_for_h_t, \
            alpha1, beta1, beta2, delta1, delta2, C_public, C_private, gamma2

def easy_as_abc_dg_rs(x, y):
    GF = galois.GF(curve_order)
    
    # Generate QAP
    Ua, Va, _, h, t, witness, U, V, W = r1cs_to_qap(curve_order, x, y, GF)
    
    powers_of_tau_for_A, \
        powers_of_tau_for_B, \
            powers_of_tau_for_h_t, \
                alpha1, beta1, beta2, delta1, delta2, C_public, C_private, gamma2 = \
        trusted_setup(GF, t, Ua, U, V, W)
    
    # Protect ZK
    r = GF(random.randint(1, curve_order - 1))
    s = GF(random.randint(1, curve_order - 1))

    # Calculate A1, B1 and B2
    A1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_A, Ua.coeffs[::-1])))
    A1 = add(
            add(
                alpha1, 
                A1
            ), 
            multiply(
                delta1, 
                int(r)
            )
        )
    B2 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_B, Va.coeffs[::-1])))
    B2 = add(
            add(
                beta2, 
                B2
            ), 
            multiply(
                delta2, 
                int(s)
            )
        )
    
    B1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_A, Va.coeffs[::-1])))
    B1 = add(
            add(
                beta1, 
                B1
            ), 
            multiply(
                delta1, 
                int(s)
            )
        )
     
    HT1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(powers_of_tau_for_h_t, h.coeffs[::-1])))
    
    sA1 = multiply(A1, int(s))
    rB1 = multiply(B1, int(r))
    rs_delta_1 = multiply(delta1, int(r*s))
    X1 = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(C_public, witness[:2])))
    C_private = reduce(add, (multiply(point, int(coeff)) for point, coeff in zip(C_private, witness[2:])))
    C1 = add(C_private, HT1)
    C1 = add(C1, sA1)
    C1 = add(C1, rB1)
    C1 = add(C1, neg(rs_delta_1))

    return A1, B2, C1, alpha1, beta2, gamma2, delta2, X1, C_public, witness
    
def test_week_8_abc_dg_rs(homework8_contract):
    A1, B2, C1, alpha1, beta2, gamma_2, delta_2, X1, C_public, witness = easy_as_abc_dg_rs(3, 4)

    assert final_exponentiate(pairing(B2, A1)) == \
        final_exponentiate(
            pairing(beta2, alpha1) *
            pairing(gamma_2, X1) *
            pairing(delta_2, C1)), "sorry, nope"
    
    assert homework8_contract.verify_witness(   fq_to_point(A1), 
                                                fq2_to_point(B2), 
                                                fq_to_point(C1), 
                                                [repr(int(el)) for el in witness[:2]],
                                                # The following are part of the trusted setup and wouldn't be shared at verification
                                                # but rather deployed onchain with the contact as constants
                                                # Left here just to make it easier for test
                                                fq_to_point(alpha1), 
                                                fq2_to_point(beta2),
                                                [fq_to_point(C_public[0]), fq_to_point(C_public[1])], 
                                                fq2_to_point(gamma_2),
                                                fq2_to_point(delta_2))

def main():
    A1, B2, C1, alpha1, beta2, gamma2, delta2, X1, _, _ = easy_as_abc_dg_rs()
    
    assert final_exponentiate(pairing(B2, A1)) == \
        final_exponentiate(
            pairing(beta2, alpha1) *
            pairing(gamma2, X1) *
            pairing(delta2, C1)), "sorry, nope"
    
if __name__ == "__main__":
    main()