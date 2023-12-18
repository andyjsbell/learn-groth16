// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.13;

contract Homework8 {
    uint256 public constant FIELD_MODULUS =
        21888242871839275222246405745257275088696311157297823662689037894645226208583;

    struct G1Point {
        uint256 X;
        uint256 Y;
    }

    struct G2Point {
        uint256[2] X;
        uint256[2] Y;
    }

    function negate(G1Point memory p) internal pure returns (G1Point memory) {
        // The prime q in the base field F_q for G1
        if (p.X == 0 && p.Y == 0) {
            return G1Point(0, 0);
        } else {
            return G1Point(p.X, FIELD_MODULUS - (p.Y % FIELD_MODULUS));
        }
    }

    function decode_result(bytes memory result) public pure returns(G1Point memory) {
        (uint256 x, uint256 y) = abi.decode(result, (uint256, uint256));

        G1Point memory C;
        C.X = x;
        C.Y = y;
        return C;
    }

    function add(G1Point memory A, G1Point memory B) public view returns(G1Point memory) {
        (bool ok, bytes memory result) = address(6).staticcall(abi.encode(A.X, A.Y, B.X, B.Y));
        require(ok, "failed that addition call");
        return decode_result(result);
    }

    function multiply(G1Point memory A, uint256 scalar) public view returns(G1Point memory) {
        (bool ok, bytes memory result) = address(7).staticcall(abi.encode(A.X, A.Y, scalar));
        require(ok, "failed that multiplication call");
        return decode_result(result);
    }
    
    function verify_witness(
        G1Point memory A1,
        G2Point memory B2,
        G1Point memory alpha1,
        G2Point memory beta2,
        G1Point[2] memory C_public,
        G2Point memory gamma2,
        G1Point memory C1,
        G2Point memory delta2,
        uint256[2] memory public_inputs
    ) public view returns (bool) {
        // pairing(B2, A1) == pairing(beta2, alpha1) + pairing(gamma2, X1) + pairing(delta2, C1)

        G1Point memory neg_A1 = negate(A1);
        G1Point memory X1 = add(multiply(C_public[0], public_inputs[0]), multiply(C_public[1], public_inputs[1]));

        uint256[24] memory input = [
            neg_A1.X,
            neg_A1.Y,
            B2.X[1],
            B2.X[0],
            B2.Y[1],
            B2.Y[0],
            alpha1.X,
            alpha1.Y,
            beta2.X[1],
            beta2.X[0],
            beta2.Y[1],
            beta2.Y[0],
            X1.X,
            X1.Y,
            gamma2.X[1],
            gamma2.X[0],
            gamma2.Y[1],
            gamma2.Y[0],
            C1.X,
            C1.Y,
            delta2.X[1],
            delta2.X[0],
            delta2.Y[1],
            delta2.Y[0]
        ];

        assembly {
            let success := staticcall(
                gas(),
                8,
                input,
                mul(24, 0x20),
                input,
                0x20
            )
            if success {
                return(input, 0x20)
            }
        }

        return false;
    }
}
