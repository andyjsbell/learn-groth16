# Problem 2
# Why does an R1CS require exactly one multiplication per row?
# Keeping things to one operation means we can achieve better efficiency, be succint my friend
# How does this relate to bilinear pairings?
# In combination with R1CS bilinear pairings provide quick verificiation of these computations

# Problem 3
# Convert the following R1CS into a QAP over real numbers, not a finite field

import numpy as np
from numpy import poly1d
import random
from scipy.interpolate import lagrange

# Taking this R1CS convert to QAP

# Define the matrices
A = np.array([[0,0,3,0,0,0],
               [0,0,0,0,1,0],
               [0,0,1,0,0,0]])

B = np.array([[0,0,1,0,0,0],
               [0,0,0,1,0,0],
               [0,0,0,5,0,0]])

C = np.array([[0,0,0,0,1,0],
               [0,0,0,0,0,1],
               [-3,1,1,2,0,-1]])

# pick random values for x and y
x = random.randint(1,1000)
y = random.randint(1,1000)

# this is our orignal formula
out = 3 * x * x * y + 5 * x * y - x- 2*y + 3# the witness vector with the intermediate variables inside
v1 = 3*x*x
v2 = v1 * y
w = np.array([1, out, x, y, v1, v2])

result = C.dot(w) == np.multiply(A.dot(w),B.dot(w))
assert result.all(), "result contains an inequality"

# Convert to QAP over real numbers
# Starting with U
# Over 3 rows
xs = [1, 2, 3]
# We have two columns that aren't zero
#x
print("x\n", lagrange(xs, [3, 0, 1]))
# 2x^2 - 9x + 10
#v1
print("v1\n", lagrange(xs, [0, 1, 0]))
# -x^2 + 4x - 3

# Which would give us a U of
# 1, out, x, y, v1, v2
U = np.array([
    [0, 0, 2, 0, -1, 0], # x^2
    [0, 0, -9, 0, 4, 0], # x^1 
    [0, 0, 10, 0, -3, 0] # x^0
])

# Next V
# We have two columns that aren't zero
#x
print("x\n", lagrange(xs, [1, 0, 0]))
#0.5x^2 - 2.5x + 3
#y
print("y\n", lagrange(xs, [0, 1, 5]))
#1.5x^2 - 3.5x + 2
# Which would give us a V of
# 1, out, x, y, v1, v2
V = np.array([
    [0, 0, 0.5, 1.5, 0, 0], # x^2
    [0, 0, -2.5, -3.5, 0, 0], # x^1 
    [0, 0, 3, 2, 0, 0] # x^0
])

# Finally W
# We have six columns that aren't zero
#1
print("1\n", lagrange(xs, [0, 0, -3]))
#-1.5x^2 + 4.5x -3
#out
print("out\n", lagrange(xs, [0, 0, 1]))
#0.5x^2 - 1.5x + 1
#x
print("x\n", lagrange(xs, [0, 0, 1]))
#0.5x^2 - 1.5x + 1
#y
print("y\n", lagrange(xs, [0, 0, 2]))
#x^2 - 3x + 2
#v1
print("v1\n", lagrange(xs, [1, 0, 0]))
#0.5x^2 - 2.5x + 3
#v2
print("v2\n", lagrange(xs, [0, 1, -1]))
#-1.5x^2 + 5.5x - 4

# Which would give us a W of
# 1, out, x, y, v1, v2
W = np.array([
    [-1.5,  0.5,  0.5,  1,  0.5, -1.5], # x^2
    [ 4.5, -1.5, -1.5, -3, -2.5,  5.5], # x^1 
    [ -3,    1,    1,   2,  3,     -4] # x^0
])

# With the original formula
# 3x^2y + 5xy - x - 2y + 3
# with x = 2 and y = 3 out withness would be
x = 2
y = 3
out = 3 * x * x * y + 5 * x * y - x- 2*y + 3 
# the witness vector with the intermediate variables inside
v1 = 3*x*x
v2 = v1 * y

witness = np.array([1, out, x, y, v1, v2])

print(np.matmul(U, witness))
#[-8 30 -16]
print(np.matmul(V, witness))
#[5.5 -15.5 12.]
print(np.matmul(W, witness))
#[-15 69. -42.]

a = poly1d([-8, 30, -16])
b = poly1d([5.5, -15.5, 12])
c = poly1d([-15, 69, -42])
t = poly1d([1, -1])*poly1d([1, -2])*poly1d([1, -3])

# Fix should not get remainder here to get h(x) 
print((a * b - c) / t)
# (poly1d([-44.,  25.]), poly1d([0.]))
# Therefore the QAP is:
# h(x) = -44x + 25 
