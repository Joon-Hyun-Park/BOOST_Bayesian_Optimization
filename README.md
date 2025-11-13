# BOOST_Bayesian_Optimization
Bayesian Optimization framework and GUI implementation for BOOST: Bayesian Optimization with Optimal Kernel and Acquisition Function Selection Technique

## BOOST GUI Release
The pre-release version (**v0.1.0**) of BOOST GUI is available for internal testing.

- **Executable (.exe)** — BOOST-GUI.exe *(Windows 10/11, 64-bit)*
- **Application (.app)** — BOOST-GUI.app *(macOS 13+, Apple Silicon)*
- **User Manual (PDF)** — BOOST_GUI_Manual.pdf *(Installation and workflow guide)*

## Code Structure

**tests** → Python scripts to evaluate the performance of BOOST and the 16 deterministic candidates
- Test_Benchmark_Functions.py → Runs tests on synthetic benchmark functions
   • use_boost = True → Runs BOOST
   • use_boost = False → Uses fixed hyperparameter set
- Test_HPOB.py → Runs tests on machine learning hyperparameter optimization tasks (HPO-B)
   • use_boost = True → Runs BOOST
   • use_boost = False → Uses fixed hyperparameter set
- _class_for_test_boost.py → Defines the class to run the BO cycle (with or without BOOST).
   Used by Test_Benchmark_Functions.py and Test_HPOB.py

**benchmarks** → Definitions of synthetic benchmark functions and HPO-B data
   *Following the HPO-B paper, users can download the raw dataset from the original source; running the provided scripts (download_hpob_data.py and hpob_handler.py) will then generate the processed .csv files used in our experiments.*
- download_hpob_data.py → Downloads and processes the HPO-B dataset
- hpob_handler.py → Processes and formats the HPO-B dataset
- Benchmark_ftn.py → Defines synthetic benchmark functions

**core** → Core classes and functions for Bayesian Optimization
- BayesianOptimization.py → Implements a single BO step
- BOOST.py → Recommends a kernel–acquisition function pair using data-in-hand
- kernels_and_acquisitions.py → Defines GP models and enumerates kernel/acquisition options

**utils** → Utility functions
- Save_results.py → Saves results

**Note: Throughout the code and results, the Lower Confidence Bound (LCB) acquisition function is referred to as UCB for convenience, following common usage in BO libraries.**
