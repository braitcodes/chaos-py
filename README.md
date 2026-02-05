# Chaos Engine

**High-Performance, Cryptographically Secure Randomness for Python.**

Chaos Engine is a specialized Python library designed to provide random selection capabilities that are both cryptographically secure and computationally efficient. It bridges the gap between Python's native `random` module (which is fast but insecure) and the `secrets` module (which is secure but can be slower and less versatile for complex data structures).

The library utilizes a custom entropy aggregation algorithm combined with low-level bitwise operations to deliver unpredictability without the overhead of string processing or heavy memory allocation.

---

## Technical Overview

The core function of Chaos Engine is to generate randomness that is statistically indistinguishable from true noise, while remaining resistant to prediction attacks. It achieves this through two main architectural decisions:

### 1. Multi-Layered Entropy Aggregation
Unlike standard generators that often rely on a single seed (like the system clock), Chaos Engine constructs a 64-bit entropy pool by harvesting data from **10 distinct system sources** in real-time. This ensures that even if one source is compromised or predictable (e.g., a frozen system clock), the other layers maintain the integrity of the randomness.

The engine collects the following data points for every decision:
* **CSPRNG:** `secrets.randbits` (Operating System's cryptographic source).
* **Kernel Noise:** `os.urandom` (Raw bytes from the OS driver).
* **High-Precision Time:** `time.time_ns` (Nanoseconds, bit-rotated to avoid linearity).
* **Memory State:** `id(object)` (Address of a transient object in RAM).
* **Process Context:** `os.getpid` (Cached Process ID).
* **Runtime State:** `gc.get_count` (Garbage Collector generation counts).
* **Network/Node Identity:** `uuid.uuid4` (Clock sequence and node ID).
* **Deterministic Chaos:** `math.sin` applied to the CPU performance counter.
* **Hardware Instructions:** `SystemRandom` (Direct CPU RNG instructions, if available).

**The Bitwise Mixer:**
Instead of concatenating these values into strings and hashing them (which consumes CPU cycles and memory), Chaos Engine mixes these sources using **XOR (`^`)** and **Bitwise Shift** operations. Finally, it applies a Knuth-style multiplicative hash to ensure an "avalanche effect," where a single bit change in the input results in a drastic change in the output.

### 2. Zero-Copy Matrix Selection
A common bottleneck in random libraries occurs when selecting items from multi-dimensional arrays (matrices). Standard approaches flatten the matrix into a single list, duplicating the data in RAM.

Chaos Engine uses **Virtual Indexing**. When a matrix is passed to the `pick()` function:
1.  The engine calculates the total number of elements ($Rows \times Columns$).
2.  It selects a random index within that total range.
3.  It mathematically maps that 1D index back to 2D coordinates ($Row, Column$) using integer division and modulus operations.

This allows the library to pick a random item from a dataset of millions of items with **O(1) memory usage**, as no new lists are created.

---

## Comparison: Chaos vs. Standard Libraries

| Feature | random (Native) | secrets (Std Lib) | Chaos Engine |
| :--- | :--- | :--- | :--- |
| **Algorithm** | Mersenne Twister | OS CSPRNG | Hybrid Bitwise Mixer |
| **Predictability** | High (Deterministic) | Low (Secure) | **Extremely Low (Multi-Source)** |
| **Performance** | Fast | Slower | **Very Fast** |
| **Memory Efficiency** | Low (Flattens lists) | Low (Flattens lists) | **High (Zero-Copy)** |
| **Ideal Use Case** | Non-critical simulations | Passwords/Keys | **Production Games, Shuffling, Data Sampling** |

---

## Installation

Currently, Chaos Engine is distributed as a standalone module. Place the `chaos.py` file into your project directory.

```python
import chaos
```
---

## Core Functions & Usage

The library provides a complete suite of tools for secure randomization.

### 1. The `pick()` Selector
Polymorphic function that automatically detects the input type and applies the most efficient selection strategy.

```python
# Select from a list
fruits = ["Apple", "Banana", "Grape", "Orange"]
print(chaos.pick(fruits))

# Select from a string
print(chaos.pick("ABCDEF"))

# Zero-Copy Matrix Selection (O(1) Memory)
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
print(chaos.pick(matrix))
```
### 2. True Shuffling
Performs an in-place Fisher-Yates shuffle using hardware entropy. Unlike random.shuffle, this cannot be reverse-engineered by predicting the seed.

```python
cards = ["Ace", "King", "Queen", "Jack", "10"]
chaos.shuffle(cards)
print(cards) 
# Result: ["Queen", "10", "Ace", "Jack", "King"]
```
### 3. Secure Integers
Generates a random integer $N$ such that $a \le N \le b$. It uses direct modular arithmetic to avoid the floating-point bias common in standard RNGs.

```python
# Rolling a D20 dice securely
d20 = chaos.randint(1, 20)
print(f"You rolled: {d20}")
```

### 4. Unique Sampling
Selects $k$ unique elements from a population without replacement. It utilizes a partial shuffle algorithm ($O(k)$), making it far more memory-efficient than shuffling the entire population.

```python
# Select 6 unique numbers from 1 to 60 (Lottery style)
numbers = list(range(1, 61))
winners = chaos.sample(numbers, 6)
print(winners)
```

### 5. High-Speed Boolean (Coin Flip)
An ultra-optimized function that checks a single bit of entropy. It eliminates arithmetic operations, providing the fastest possible `True`/`False` decision mechanism for simulations.

```python
if chaos.coin():
    print("Heads!")
else:
    print("Tails!")
```

### 6. Security Tokens
Generates a cryptographically strong random hex string. It combines OS entropy with 9 other system noise sources ("Defense in Depth"), making it ideal for API keys and session tokens.

```python
# Generate a 32-byte (64 char) secure token
api_key = chaos.token_hex(32)
print(api_key)
# Ex: f4a1d8b9e3...
```
