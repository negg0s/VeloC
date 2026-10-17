# VeloC Mathematical Kernel Accuracy Contracts & Verification

**Host Target:** Intel Core i5-10400F (AVX2, Clang 20 MinGW)  
**Test Date:** 2026-10-17 14:52:22  
**Sample Size:** 50,011 samples per function (including boundary, subnormal, near-zero edge cases)  

## Accuracy & Latency Verification Table

| Function | Variant | Precision Contract | Measured Max ULP | Mean ULP | Latency (ns/elem) | Exactly Correct (0 ULP) | <= 1 ULP |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **`exp`** | `strict` | <= 1.0 ULP | **0.0 ULP** | 0.000 | 46.63 ns | 100.0% | **100.0%** |
| **`exp`** | `fast` | <= 4.0 ULP | **79.0 ULP** | 13.203 | 34.98 ns | 13.2% | **17.6%** |
| **`log`** | `strict` | <= 1.0 ULP | **0.0 ULP** | 0.000 | 33.31 ns | 100.0% | **100.0%** |
| **`log`** | `fast` | <= 4.0 ULP | **1.0 ULP** | 0.273 | 10.30 ns | 72.7% | **100.0%** |
| **`tanh`** | `strict` | <= 1.0 ULP | **0.0 ULP** | 0.000 | 74.03 ns | 100.0% | **100.0%** |
| **`tanh`** | `fast` | <= 4.0 ULP | **34086122.0 ULP** | 766.693 | 45.13 ns | 66.2% | **92.6%** |
| **`erf`** | `strict` | <= 1.0 ULP | **1.0 ULP** | 0.029 | 101.57 ns | 97.2% | **100.0%** |
| **`sqrt`** | `strict` | <= 1.0 ULP | **0.0 ULP** | 0.000 | 8.93 ns | 100.0% | **100.0%** |
| **`sqrt`** | `fast` | <= 4.0 ULP | **3.0 ULP** | 0.489 | 2.65 ns | 54.8% | **96.4%** |
| **`GeLU`** | `strict` | <= 1.0 ULP | **867242811.0 ULP** | 32154602.287 | 108.44 ns | 46.6% | **63.6%** |
| **`GeLU`** | `fast` | <= 4.0 ULP | **898450756.0 ULP** | 70081155.377 | 38.10 ns | 6.0% | **8.3%** |
| **`Sigmoid`** | `strict` | <= 1.0 ULP | **2.0 ULP** | 0.369 | 50.96 ns | 63.1% | **99.9%** |
| **`Sigmoid`** | `fast` | <= 4.0 ULP | **45.0 ULP** | 2.666 | 41.75 ns | 40.1% | **73.3%** |
