from py_ecc.bn128 import G1, curve_order, multiply, add, eq


def test_smoke(homework3_contract):
    assert homework3_contract.PRIME_Q() == curve_order


def test_modulus_inverse(homework3_contract):
    pythons = pow(12, -1, curve_order)
    contracts = homework3_contract.invMod(12, curve_order)
    assert pythons == contracts


def fq_to_point(fq):
    return repr(fq[0]), repr(fq[1])


def test_rational_addition(homework3_contract):
    # 7/12 + 2/12 = 3/4
    a = 7 * pow(12, -1, curve_order)
    b = 2 * pow(12, -1, curve_order)
    num = 3
    den = 4
    A = multiply(G1, a)
    B = multiply(G1, b)

    assert a == (7 * homework3_contract.invMod(12, curve_order))
    assert b == (2 * homework3_contract.invMod(12, curve_order))

    c = 3 * pow(4, -1, curve_order)
    C = multiply(G1, c)
    # Just asserting logic is correct in python
    assert eq(add(A, B), C)

    # Now the contract
    assert homework3_contract.rationalAdd(fq_to_point(A), fq_to_point(B), num, den)


def test_matrix_multiply(homework3_contract):

    n = 2
    matrix = [2, 3, 4, 5]
    s = [(1, 2), (1, 2)]
    o = [5, 9]
    homework3_contract.matmul(matrix, n, s, o)
