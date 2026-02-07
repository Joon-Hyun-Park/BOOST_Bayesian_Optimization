# BOOST: Bayesian Optimization with Optimal Kernel and Acquisition Function Selection Technique

Implementation of **BOOST**, a novel Bayesian Optimization framework designed to automatically select the optimal kernel and acquisition function pair during the optimization process.

## Code Structure

### tests
→ Python scripts to evaluate the performance of BOOST and the 16 deterministic candidates
- `Test_Benchmark_Functions.py` → Runs tests on synthetic benchmark functions
   - use_boost = True → Runs BOOST
   - use_boost = False → Uses fixed hyperparameter set

- `Test_HPOB_chem_eng.py` → Runs tests on machine learning hyperparameter optimization tasks (HPO-B) and chemical engineering tasks
   - use_boost = True → Runs BOOST
   - use_boost = False → Uses fixed hyperparameter set

- `_class_for_test_boost.py` → Defines the class to run the BO cycle (with or without BOOST).
   Used by Test_Benchmark_Functions.py and Test_HPOB.py

### benchmarks
→ Definitions of synthetic benchmark functions and datasets used in the experiments, including synthetic functions, processed HPO-B data, and chemical engineering datasets.
All experiments directly use the processed CSV files provided in this repository.
- `Benchmark_ftn.py` → Defines synthetic benchmark functions

### core
→ Core classes and functions for Bayesian Optimization
- `BayesianOptimization.py` → Implements a single BO step
- `BOOST.py` → Recommends a kernel–acquisition function pair using data-in-hand
- `kernels_and_acquisitions.py` → Defines GP models and enumerates kernel/acquisition options

### utils
→ Utility functions
- `Save_results.py` → Saves results

Note: Throughout the code and results, the Lower Confidence Bound (LCB) acquisition function is referred to as UCB for convenience, following common usage in BO libraries.

## Data Structure

### Note on Iteration Indexing
- In the data files, iteration indexing starts at 0 and includes the initial samples.
- In the main paper, iteration counts are reported excluding the initial samples.

Example:
- Data file iteration 0–9  → Initial 10 samples
- Data file iteration 10–99 → Iteration 0–89 in the main paper

### File Types
1. Files ending with `_results.xlsx`
- File name format: (objective)_(kernel_acq)_results.xlsx
- For BOOST: "recommended" replaces kernel/acq name
- Summarizes regret (mean and std) for each iteration

### Directory Structure
1. Synthetic Benchmark Functions
   - 1.1 BOOST
   - 1.2 16_Deterministic
2. Machine Learning Hyperparameter Optimization
   - 2.1 BOOST
   - 2.2 16_Deterministic
3. Chemical Engineering Experiments
   - 3.1 BOOST
   - 3.2 16_Deterministic
A. Additional Results → Data referenced in technical appendix (excluding ‘Default,’ which is included in the BOOST data).

### Notes
- Throughout the code and results, the Lower Confidence Bound (LCB) acquisition function is referred to as UCB for convenience, following common usage in BO libraries.

## Dataset Citation

When using the benchmark datasets, please cite the following works.

### HPO-B

```
@article{arango2021hpo,
  title={Hpo-b: A large-scale reproducible benchmark for black-box hpo based on openml},
  author={Arango, Sebastian Pineda and Jomaa, Hadi S and Wistuba, Martin and Grabocka, Josif},
  journal={arXiv preprint arXiv:2106.06257},
  year={2021}
}
```

### Chemical Engineering Datasets

```
@article{liang2021benchmarking,
  title={Benchmarking the performance of Bayesian optimization across multiple experimental materials science domains},
  author={Liang, Qiaohao and Gongora, Aldair E and Ren, Zekun and Tiihonen, Armi and Liu, Zhe and Sun, Shijing and Deneault, James R and Bash, Daniil and Mekki-Berrada, Flore and Khan, Saif A and others},
  journal={npj Computational Materials},
  volume={7},
  number={1},
  pages={188},
  year={2021},
  publisher={Nature Publishing Group UK London}
}
```

#### AgNP dataset

```
@article{mekki2021two,
  title={Two-step machine learning enables optimized nanoparticle synthesis},
  author={Mekki-Berrada, Flore and Ren, Zekun and Huang, Tan and Wong, Wai Kuan and Zheng, Fang and Xie, Jiaxun and Tian, Isaac Parker Siyu and Jayavelu, Senthilnath and Mahfoud, Zackaria and Bash, Daniil and others},
  journal={npj Computational Materials},
  volume={7},
  number={1},
  pages={1--10},
  year={2021},
  publisher={Nature Publishing Group}
}
```

#### P3HT/CNT dataset

```
@article{bash2021multi,
title={Multi-Fidelity High-Throughput Optimization of Electrical Conductivity in P3HT-CNT Composites},
author={Bash, Daniil and Cai, Yongqiang and Chellappan, Vijila and Wong, Swee Liang and Yang, Xu and Kumar, Pawan and Tan, Jin Da and Abutaha, Anas and Cheng, Jayce JW and Lim, Yee-Fun and others},
journal={Advanced Functional Materials},
pages={2102606},
year={2021},
publisher={Wiley Online Library}
}
```
## Graphical User Interface (Beta)

To enhance accessibility, we provide a GUI version of BOOST for user convenience and visualization. This allows users to utilize the algorithm easily without complex code configurations.

* **Source Code:** The source code for the GUI is located in the `BOOST_GUI/` folder.
* **Standalone Executables:** If you do not have a Python environment, you can download the pre-compiled applications (`.exe` / `.app`) from the Releases page.

Note: The experiments presented in the paper were conducted using the scripts in the experiments/ folder, not the GUI.


## License

[MIT license](https://opensource.org/license/mit/)