# Changelog

All notable changes to the "Chaos Engine" project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-05
### Added
- Initial public release.
- **Core:** `pick()` function with polymorphic support (Lists, Strings, Ranges).
- **Optimization:** Zero-Copy architecture for Matrix (2D Array) selection ($O(1)$ memory).
- **Entropy:** 10-layer entropy aggregation system (Hardware, OS, Time, Memory, CPU Noise).

### Security
- Implemented "Defense in Depth" strategy combining `secrets`, `os.urandom`, and system jitter.
- Constant-time execution path for boolean checks to prevent timing attacks.

## [1.0.1] - 2026-02-05
### Added
- **Utils:** Added `shuffle()` for in-place list mixing using Fisher-Yates algorithm.
- **Utils:** Added `randint(a, b)` for secure integer generation.
- **Utils:** Added `sample(pop, k)` for unique selection without replacement.
- **Utils:** Added `coin()` for high-speed boolean decision (optimized bitwise check).
- **Utils:** Added `token_hex(bytes)` for cryptographic token generation.