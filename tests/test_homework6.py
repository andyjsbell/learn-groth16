from py_ecc.bn128 import G1, G2, curve_order, multiply, add, eq, neg, pairing, G12
import numpy as np
import random

def create_proof(p):
    # 5x^3 - 4y^2 * x^2 + 13x * y^2 + x^2 - 10y
    A = np.array([
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  1,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  -4, 0,  0,  0]
    ]);
    B = np.array([
        [ 0, 0, 1, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 1, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 1, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 1, 0, 0],
        [ 0, 0, 0, 0, 0, 1, 0, 0]
        ]);
    C= np.array([
        [ 0,  0,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  1],
        [ 0,  1,  0, 10, -1,  0, -5,  -13]
        ]);

    x = random.randint(1,1000)
    y = random.randint(1,1000)

    v1 = x * x % p
    v2 = y * y % p
    v3 = v1 * x % p
    v4 = v2 * x % p
    # out = 5v3 - 4v1 * v2 + 13v4 + v1 - 10y
    out = 5*v3 - 4*v1*v2 + 13*v4 + v1 - 10*y % p
    witness = np.array([1, out, x, y, v1, v2, v3, v4]);
    result = C.dot(witness) % p == A.dot(witness) % p * B.dot(witness) % p
    assert result.all(), "result contains an inequality"

    # create S and multiply through to get L, R and O
    s = witness.reshape(-1, 1)
    LS1 = np.matmul(A, s)
    RS2 = np.matmul(B, s)
    OS1 = np.matmul(C, s)

    # Encode to G1 and G2 points
    encoded_LS1 = [[multiply(G1, element % p) if element != 0 else 0 for element in row] for row in LS1]
    encoded_RS2 = [[multiply(G2, element % p) if element != 0 else 0 for element in row] for row in RS2]
    encoded_OS1 = [[multiply(G1, element % p) if element != 0 else 0 for element in row] for row in OS1]
    
    return (encoded_LS1, encoded_RS2, encoded_OS1)

def fq_to_point(fq):
    return [repr(fq[0]), repr(fq[1])]

def fq2_to_point(fq):
    return [[repr(fq[0].coeffs[0]), repr(fq[0].coeffs[1])], [repr(fq[1].coeffs[0]), repr(fq[1].coeffs[1])]]

def test_week_6(homework6_contract):
    # create proof
    LS1, RS2, OS1 = create_proof(curve_order)
    # verify by pairing RS2 with LS1 and G2 with OS1 
    assert eq(pairing(RS2[0][0], LS1[0][0]), pairing(G2, OS1[0][0]))
    # verify a couple of points ;)
    homework6_contract.verify_witness(fq_to_point(LS1[0][0]), fq2_to_point(RS2[0][0]), fq_to_point(OS1[0][0]))
    homework6_contract.verify_witness(fq_to_point(LS1[1][0]), fq2_to_point(RS2[1][0]), fq_to_point(OS1[1][0]))
