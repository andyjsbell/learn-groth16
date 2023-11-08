from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, pairing, G12

def fq_to_point(fq):
    return [repr(fq[0]), repr(fq[1])]

def fq2_to_point(fq):
    return [[repr(fq[0].coeffs[0]), repr(fq[0].coeffs[1])], [repr(fq[1].coeffs[0]), repr(fq[1].coeffs[1])]]

def test_week_4(homework4_contract):
    # A1*B2 = alpha_1 * beta_2 + X1 * gamma_2 + C1 * delta_2
    # X1 = x1*G1 + x2*G1 + x3*G1
    # pairing(multiply(G1, 2), multiply(G2, 27)) = pairing(multiply(G1,2), multiply(G2, 3)) + pairing(multiply(G1,1+1+1), multiply(G2, 4)) + pairing(multiply(G1,2), multiply(G2, 6))
    # 2 * 27 = (2 * 3) + (3 * 4) + (6 * 6)
    x1 = 1
    x2 = 1
    x3 = 1
    A = fq_to_point(multiply(G1, 2))
    B = fq2_to_point(multiply(G2, 27))
    C = fq_to_point(multiply(G1, 6))

    assert homework4_contract.verify(A, B, C, x1, x2, x3)