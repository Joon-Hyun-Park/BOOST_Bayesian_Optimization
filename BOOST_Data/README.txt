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
