# Groth16

### Learning ZK by implementing Groth16  

Verifier: [contracts/Homework8.sol](contracts/Homework8.sol)  
Prover: [tests/test_homework8.py](tests/test_homework8.py)

### Getting started
```bash
python -m venv ape-devel
source ape-devel/bin/activate
pip install eth-ape'[recommended-plugins]'
pip install galois
```

### Tests
Test all
```bash
ape test
```
Test Groth16
```bash
ape test tests/test_homework8.py
```
