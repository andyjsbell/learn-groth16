// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.13;
contract Homework3 {

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

    struct ECPoint {
        uint256 x;
        uint256 y;
    }

    function decode_result(bytes memory result) public pure returns(ECPoint memory) {
        (uint256 x, uint256 y) = abi.decode(result, (uint256, uint256));

        ECPoint memory C;
        C.x = x;
        C.y = y;
        return C;
    }

    function eq(ECPoint memory A, ECPoint memory B) public pure returns (bool) {
        return A.x == B.x && A.y == B.y;
    }

    function add(ECPoint calldata A, ECPoint calldata B) public view returns(ECPoint memory) {
        (bool ok, bytes memory result) = address(6).staticcall(abi.encode(A.x, A.y, B.x, B.y));
        require(ok, "failed that addition call");
        return decode_result(result);
    }

    function multiply(ECPoint memory A, uint256 scalar) public view returns(ECPoint memory) {
        (bool ok, bytes memory result) = address(7).staticcall(abi.encode(A.x, A.y, scalar));
        require(ok, "failed that multiplication call");
        return decode_result(result);
    }

    uint256 constant PRIME_Q = 21888242871839275222246405745257275088548364400416034343698204186575808495617;

    function s(ECPoint calldata A) public pure returns(bool) {
        return true;
    }

    function rationalAdd(ECPoint calldata A, ECPoint calldata B, uint256 num, uint256 den) public view returns (bool verified) {
        // return true if the prover knows two numbers that add up to num/den
        // First things first, we have homomorphism of rational number to a finite field
        // num * den^-1 % curve_order
        uint256 curve_order = PRIME_Q;
        uint256 a = num * invMod(den, curve_order);
        // under EC points we would be able to verify this by:
        // multiply(G1, a) = add(A, B)
        ECPoint memory G1;
        G1.x = 1;
        G1.y = 2;
        verified = eq(multiply(G1, a), add(A, B));
    }

    function matmul(uint256[] calldata matrix,
        uint256 n, // n x n for the matrix
        ECPoint[] calldata s, // n elements
        uint256[] calldata o // n elements
    ) public pure returns (bool verified) {
        // revert if dimensions don't make sense or the matrices are empty
        require(matrix.length == 0 || n == 0, "Empty");
        require(matrix.length == n, "Matrix and element mismatch");
        require(s.length == n, "s and element mismatch");
        require(o.length == n, "o and element mismatch");

        // Multiplication of matrix by EC.x
        uint256[] memory Ms = new uint256[](n);
        for (uint256 i = 0; i < n; i++) {
            Ms[i] = 0;
            for (uint256 j = 0; j < n; j++) {
                Ms[i] += matrix[i] * s[j].x;
            }
        }

        // This can be removed, for debugging
        require(Ms.length == n, "Mismatch in lengths");

        // return true if Ms == o elementwise. You need to do n equality checks. If you're lazy, you can hardcode n to 3, but it is suggested that you do this with a for loop
        bool equal = false;

        for (uint256 i = 0; i < n; i++) {
            equal = (Ms[i] == o[i]);
            if (!equal) break;
        }

        return equal;
    }
}