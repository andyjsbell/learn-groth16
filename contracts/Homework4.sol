// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.13;

contract Homework4 {

    uint256 constant public FIELD_MODULUS = 21888242871839275222246405745257275088696311157297823662689037894645226208583;
    
    function multiply(G1Point memory A, uint256 scalar) public view returns(G1Point memory) {
        (bool ok, bytes memory result) = address(7).staticcall(abi.encode(A.X, A.Y, scalar));
        require(ok, "failed that multiplication call");
        return decode_result(result);
    }

    function decode_result(bytes memory result) public pure returns(G1Point memory) {
        (uint256 x, uint256 y) = abi.decode(result, (uint256, uint256));

        G1Point memory C;
        C.X = x;
        C.Y = y;
        return C;
    }

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

    function verify(
        G1Point memory A,
        G2Point memory B,
        G1Point memory C,
        uint256 x1,
        uint256 x2,
        uint256 x3
    ) public view returns (bool) {
        G1Point memory neg_A = negate(A);
        G1Point memory G1 = G1Point(1, 2);
        G1Point memory X1 = multiply(G1, x1 + x2 + x3);

        (G1Point memory alpha_1, G2Point memory beta_2, G2Point memory gamma_2, G2Point memory delta_2) = verifier_keys();
        
        uint256[24] memory input = [
            neg_A.X,
            neg_A.Y,
            B.X[1],
            B.X[0],
            B.Y[1],
            B.Y[0],
            alpha_1.X,
            alpha_1.Y,
            beta_2.X[1],
            beta_2.X[0],
            beta_2.Y[1],
            beta_2.Y[0],
            X1.X,
            X1.Y,
            gamma_2.X[1],
            gamma_2.X[0],
            gamma_2.Y[1],
            gamma_2.Y[0],
            C.X,
            C.Y,
            delta_2.X[1],
            delta_2.X[0],
            delta_2.Y[1],
            delta_2.Y[0]
        ];

        assembly {
            let success := staticcall(gas(), 8, input, mul(24, 0x20), input, 0x20)
            if success { return(input, 0x20) }
        }

        return false;
    }

    // alpha_1, beta_2, gamma_2, delta_2
    function verifier_keys() view internal returns (G1Point memory, G2Point memory, G2Point memory, G2Point memory) {
        return (
            // G1 * 2 - alpha_1
            multiply(G1Point(1, 2), 2),
            // G2 * 3 - beta_2
            G2Point(
                [   
                    uint256(2725019753478801796453339367788033689375851816420509565303521482350756874229), 
                    uint256(7273165102799931111715871471550377909735733521218303035754523677688038059653)
                ],
                [
                    uint256(2512659008974376214222774206987427162027254181373325676825515531566330959255), 
                    uint256(957874124722006818841961785324909313781880061366718538693995380805373202866)
                ]
            ),
            // G2 * 4 - gamma_2
            G2Point(
                [
                    uint256(18936818173480011669507163011118288089468827259971823710084038754632518263340), 
                    uint256(18556147586753789634670778212244811446448229326945855846642767021074501673839)
                ],
                [
                    uint256(18825831177813899069786213865729385895767511805925522466244528695074736584695), 
                    uint256(13775476761357503446238925910346030822904460488609979964814810757616608848118)
            ]),
            // G2 * 6 - delta_2
            G2Point(
                [
                    uint256(10191129150170504690859455063377241352678147020731325090942140630855943625622), 
                    uint256(12345624066896925082600651626583520268054356403303305150512393106955803260718)
                ],
                [
                    uint256(16727484375212017249697795760885267597317766655549468217180521378213906474374), 
                    uint256(13790151551682513054696583104432356791070435696840691503641536676885931241944)
                ]
            ));
    }
}
