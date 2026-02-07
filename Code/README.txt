Code Structure

tests → Python scripts to evaluate the performance of BOOST and the 16 deterministic candidates
- Test_Benchmark_Functions.py → Runs tests on synthetic benchmark functions
   • use_boost = True → Runs BOOST
   • use_boost = False → Uses fixed hyperparameter set
- Test_HPOB_chem_eng.py → Runs tests on machine learning hyperparameter optimization tasks (HPO-B) and chemical engineering tasks
   • use_boost = True → Runs BOOST
   • use_boost = False → Uses fixed hyperparameter set
- _class_for_test_boost.py → Defines the class to run the BO cycle (with or without BOOST).
   Used by Test_Benchmark_Functions.py and Test_HPOB.py

benchmarks → Definitions of synthetic benchmark functions and datasets used in the experiments, including synthetic functions, processed HPO-B data, and chemical engineering datasets.
- Benchmark_ftn.py → Defines synthetic benchmark functions

core → Core classes and functions for Bayesian Optimization
- BayesianOptimization.py → Implements a single BO step
- BOOST.py → Recommends a kernel–acquisition function pair using data-in-hand
- kernels_and_acquisitions.py → Defines GP models and enumerates kernel/acquisition options

utils → Utility functions
- Save_results.py → Saves results

Note: Throughout the code and results, the Lower Confidence Bound (LCB) acquisition function is referred to as UCB for convenience, following common usage in BO libraries.
