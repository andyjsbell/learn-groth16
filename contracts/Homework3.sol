// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.13;
contract Homework3 {

    uint256 constant public CURVE_ORDER = 21888242871839275222246405745257275088548364400416034343698204186575808495617;

    function invMod(uint256 _x, uint256 _pp) public pure returns (uint256) {
        require(_x != 0 && _x != _pp && _pp != 0, "Invalid number");
        uint256 q = 0;
        uint256 newT = 1;
        uint256 r = _pp;
        uint256 t;
        while (_x != 0) {
            t = r / _x;
            (q, newT) = (newT, addmod(q, (_pp - mulmod(t, newT, _pp)), _pp));
            (r, _x) = (_x, r - t * _x);
        }

        return q;
    }

    struct G1Point {
        uint256 X;
        uint256 Y;
    }

    function decode_result(bytes memory result) public pure returns(G1Point memory) {
        (uint256 x, uint256 y) = abi.decode(result, (uint256, uint256));

        G1Point memory C;
        C.X = x;
        C.Y = y;
        return C;
    }

    function eq(G1Point memory A, G1Point memory B) public pure returns (bool) {
        return A.X == B.X && A.Y == B.Y;
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

    function rationalAdd(G1Point calldata A, G1Point calldata B, uint256 num, uint256 den) public view returns (bool verified) {
        // return true if the prover knows two numbers that add up to num/den
        // First things first, we have homomorphism of rational number to a finite field
        // num * den^-1 % curve_order
        uint256 curve_order = CURVE_ORDER;
        uint256 a = num * invMod(den, curve_order);
        // under EC points we would be able to verify this by:
        // multiply(G1, a) = add(A, B)
        G1Point memory G1 = G1Point(1, 2);
        verified = eq(multiply(G1, a), add(A, B));
    }

    function matmul(uint256[] calldata matrix,
        uint256 n, // n x n for the matrix
        G1Point[] calldata s, // n elements
        uint256[] calldata o // n elements
    ) public view returns (bool verified) {
        // revert if dimensions don't make sense or the matrices are empty
        require(matrix.length > 0 || n != 0, "Empty");
        require(matrix.length == n * n, "Matrix and element mismatch");
        require(s.length == n, "s and element mismatch");
        require(o.length == n, "o and element mismatch");

        G1Point memory G1 = G1Point(1, 2);
        G1Point[] memory points = new G1Point[](n);

        for (uint256 row = 0; row < n; row++) {
            G1Point memory p = multiply(G1, CURVE_ORDER);
            for (uint256 col = 0; col < n; col++) {
                uint256 number = matrix[row * n + col];
                p = add(p, multiply(s[col], number));
            }
            points[row] = p;
        }

        // Verify elements in `o`
        for (uint256 i = 0; i < n; i++) {
            verified = eq(points[i], multiply(G1, o[i]));
            if (!verified) return verified;
        }

        return verified;
    }
}
