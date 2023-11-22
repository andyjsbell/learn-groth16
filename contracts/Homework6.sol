// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.13;

contract Homework6 {
    
    struct G1Point {
        uint256 X;
        uint256 Y;
    }

    struct G2Point {
        uint256[2] X;
        uint256[2] Y;
    }

    // L[S]1 hadamard product R[S]2 = O[S]12
    function verify_witness(G1Point memory L, G2Point memory R, G1Point memory O) public view returns (bool) {
        // static call takes G1, G2, G1, G2 and returns 0 if the pairing(G1, G2) == pairing(G1, G2)
        G2Point memory G2 = G2Point(
            [   
                uint256(10857046999023057135944570762232829481370756359578518086990519993285655852781), 
                uint256(11559732032986387107991004021392285783925812861821192530917403151452391805634)
            ],
            [
                uint256(8495653923123431417604973247489272438418190587263600148770280649306958101930), 
                uint256(4082367875863433681332203403145435568316851327593401208105741076214120093531)
            ]
        );

        uint256[12] memory input = [
            L.X,
            L.Y,
            R.X[1],
            R.X[0],
            R.Y[1],
            R.Y[0],
            O.X,
            O.Y,
            G2.X[1],
            G2.X[0],
            G2.Y[1],
            G2.Y[0]
        ];

        assembly {
            let success := staticcall(gas(), 8, input, mul(12, 0x20), input, 0x20)
            if success { return(input, 0x20) }
        }

        return false;
    }
}
