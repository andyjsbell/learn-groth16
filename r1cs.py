import numpy as np
import random

def problem_1(p):
    # 5x^3 - 4y^2 * x^2 + 13x * y^2 + x^2 - 10y
    # Constraint 1 -> v1 = x * x
    # 5x * v1 - 4y^2 * v1 + 13x * y^2 + v1 - 10y
    # Constraint 2 -> v2 = y * y
    # 5x * v1 - 4v1 * v2 + 13x * v2 + v1 - 10y
    # Constraint 3 -> v3 = x * v1
    # Constraint 4 -> v4 = x * v2
    # out = 5v3 - 4v1 * v2 + 13v4 + v1 - 10y
    # out - 5v3 - 13v4 - v1 + 10y = -4v1 * v2
    # witness [1, 0, x, y, v1, v2, v3, v4]

    # lhs -> x, y, x, x, -4v1
    A = np.array([
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  1,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  1,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  -4, 0,  0,  0]
    ]);
    # rhs -> x, y, v1, v2, v2
    B = np.array([
        [ 0, 0, 1, 0, 0, 0, 0, 0],
        [ 0, 0, 0, 1, 0, 0, 0, 0],
        [ 0, 0, 0, 0, 1, 0, 0, 0],
        [ 0, 0, 0, 0, 0, 1, 0, 0],
        [ 0, 0, 0, 0, 0, 1, 0, 0]
        ]);
    # out -> v1, v2, v3, v4, (-5v3, -13v4, -v1 + 10y) 
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

def problem_2(p):
    
#     fn main(x: field, y: field) -> field {
#       assert!(y == 0 || y == 1 || y == 2);
#       if (y == 0) {
# 		    return x; 
# 	    }
# 	    else if (y == 1) {
# 	        return x**2;
# 	    } 
# 	    else {
# 	        return x**3;
# 	    }
#     }

#   the assert can be expressed as: 
#   y(y - 1)(y - 2) = 0
#   expanded as y^3 - 3y^2 + 2y = 0
#   v1 = y * y
#   out = y * v1 - 3v1 + 2y
#   out + 3v1 - 2y = y * v1
#   Connstraint 1 -> v1 = y * y
#   Constraint 2 -> out + 3v1 - 2y = yv1
#   witness -> [1, out, x, y, v1]
#   lhs -> y, v1
    A = np.array([
        [ 0,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  1],
    ]);
#   rhs -> y, y
    B = np.array([
        [ 0,  0,  0,  1,  0],
        [ 0,  0,  0,  1,  0],
    ]);
    # v1, (out + 3v1 - 2y) where out is 0
    C = np.array([
        [ 0,  0,  0,  0,  1],
        [ 0,  0,  0,  -2,  3],
    ]);

    x = random.randint(1,1000)
    y = random.randint(1,2)

    v1 = y * y % p
    out = v1 * y - 3 * v1 + 2 * y

    witness = np.array([1, out, x, y, v1]);

    result = C.dot(witness) % p == A.dot(witness) % p * B.dot(witness) % p
    assert result.all(), "result contains an inequality"

#   the second circuit can be expressed as:
#   out = ((y - 1)(y - 2)x) / 2 + ((y - 0)(y - 2)x^2) / -1 + ((y - 0)(y - 1)x^3) / 2
#   2.out = (y - 1)(y - 2)x + -2((y - 0)(y - 2)x^2) + (y - 0)(y - 1)x^3
#   2.out = y^2x - 3yx + 2x - 2y^x^2 + 4yx^2 + y^2x^3 - yx^3
#   let v1 = yx
#   2.out = v1y - 3v1 + 2x - 2v1^2 + 4v1x + v1^2 - v1x^2
#   let v2 = v1(y - 3 - 2v1 + 4x + v1x + x^2)
#   we can then use v3 = v1x and v4 = x.x
#   so v2 = v1(y - 3 - 2v1 + 4x + v3 + v4) hence:
#   2.out - x= v1(y - 3 - 2v1 + 4x + v3 + v4)
#   therefore we have 4 constraints:
#   Connstraint 1 -> v1 = yx
#   Connstraint 2 -> v3 = v1x
#   Connstraint 3 -> v4 = xx
#   Connstraint 4 -> 2.out - 2x = v1(y - 3 - 2v1 + 4x + v3 + v4)
#   witness -> [1, out, x, y, v1, v3, v4]

    # lhs -> y, v1, x, v1
    A = np.array([
        [ 0,  0,  0,  1,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  1,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  1,  0,  0],
    ]);
    # rhs -> x, x, x, (y, -3, -2v, 4x, v3, v4)
    B = np.array([
        [ 0, 0, 1, 0, 0, 0, 0],
        [ 0, 0, 1, 0, 0, 0, 0],
        [ 0, 0, 1, 0, 0, 0, 0],
        [ -3, 0, 4, 1, -2, 1, 1],
    ]);
    # out -> v1, v2, v3, (2.out - 2x)
    C= np.array([
        [ 0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  1,  0],
        [ 0,  0,  0,  0,  0,  0,  1],
        [ 0,  2,  -2,  0,  0,  0,  0],
        ]);

    x = random.randint(1,1000)
    y = random.randint(1,1000)

    v1 = y * x % p
    v3 = v1 * x % p
    v4 = x * x % p
    # out = (v1(y - 3 - 2v1 + 4x + v3 + v4) + 2x) / 2
    out = (v1 * (y - 3 - 2*v1 + 4 * x + v3 + v4) + 2*x) * pow(2,-1,p) % p
    
    witness = np.array([1, out, x, y, v1, v3, v4]);

    result = C.dot(witness) % p == A.dot(witness) % p * B.dot(witness) % p
    assert result.all(), "result contains an inequality"

def main():
    p = 1033
    problem_1(p)
    problem_2(p)

if __name__ == "__main__":
    main()