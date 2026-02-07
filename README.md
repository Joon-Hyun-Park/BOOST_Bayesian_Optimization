# BOOST: Bayesian Optimization with Optimal Kernel and Acquisition Function Selection Technique

Implementation of **BOOST**, a novel Bayesian Optimization framework designed to automatically select the optimal kernel and acquisition function pair during the optimization process.

## 📂 Repository Structure

The repository is organized into four main directories:

```text
BOOST_Bayesian_Optimization/
├── benchmarks/              # Benchmark functions and datasets (synthetic & real-world)
│   ├── Benchmark_ftn.py     # Definitions of synthetic benchmark functions
│   └── (CSV files)          # Processed HPO-B and Chem-Eng datasets
├── core/                    # Core BO implementation
│   ├── BayesianOptimization.py  # Single BO step implementation
│   ├── BOOST.py                 # Kernel-Acquisition pair recommendation logic
│   └── kernels_and_acquisitions.py # GP models and candidates
├── tests/                   # Scripts to evaluate performance
│   ├── Test_Benchmark_Functions.py # Runs tests on synthetic functions
│   ├── Test_HPOB_chem_eng.py       # Runs tests on HPO and chemical engineering tasks
│   └── _class_for_test_boost.py    # BO cycle class used by test scripts
└── utils/                   # Utility functions
    └── Save_results.py      # Result saving functionality

## Data Structure

Note on Iteration Indexing
- In the data files, iteration indexing starts at 0 and includes the initial samples.
- In the main paper, iteration counts are reported excluding the initial samples.

Example:
  • Data file iteration 0–9  → Initial 10 samples
  • Data file iteration 10–99 → Iteration 0–89 in the main paper

File Types
1. Files ending with "_results.xlsx"
   • File name format: (objective)_(kernel_acq)_results.xlsx
   • For BOOST: "recommended" replaces kernel/acq name
   • Summarizes regret (mean and std) for each iteration

Directory Structure
- 1. Synthetic Benchmark Functions
   • 1.1 BOOST
   • 1.2 16_Deterministic
- 2. Machine Learning Hyperparameter Optimization
   • 2.1 BOOST
   • 2.2 16_Deterministic
- 3. Chemical Engineering Experiments
   • 3.1 BOOST
   • 3.2 16_Deterministic
- A. Additional Results → Data referenced in technical appendix (excluding ‘Default,’ which is included in the BOOST data).

Notes

- Throughout the code and results, the Lower Confidence Bound (LCB) acquisition function is referred to as UCB for convenience, following common usage in BO libraries.

## Dataset Citation

When using for Benchmark datasets, please cite the following authors for sharing their datasets.

HPO-B

@article{arango2021hpo,
  title={Hpo-b: A large-scale reproducible benchmark for black-box hpo based on openml},
  author={Arango, Sebastian Pineda and Jomaa, Hadi S and Wistuba, Martin and Grabocka, Josif},
  journal={arXiv preprint arXiv:2106.06257},
  year={2021}
}

Chemical Engineering Datasets

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

- AgNP dataset

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

-P3HT/CNT dataset

@article{bash2021multi,
title={Multi-Fidelity High-Throughput Optimization of Electrical Conductivity in P3HT-CNT Composites},
author={Bash, Daniil and Cai, Yongqiang and Chellappan, Vijila and Wong, Swee Liang and Yang, Xu and Kumar, Pawan and Tan, Jin Da and Abutaha, Anas and Cheng, Jayce JW and Lim, Yee-Fun and others},
journal={Advanced Functional Materials},
pages={2102606},
year={2021},
publisher={Wiley Online Library}
}

## License

[MIT license](https://opensource.org/license/mit/)