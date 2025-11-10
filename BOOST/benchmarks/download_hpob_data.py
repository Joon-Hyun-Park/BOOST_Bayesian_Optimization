import os
import random

import numpy as np
import pandas as pd

from hpob_handler import HPOBHandler

this_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.join(this_dir, "hpob-raw-data")
print(this_dir)


def process_v2_data(search_space, save_to_excel=True, round_digits=5):
    random.seed(1)
    np.random.seed(1)
    # HPOBHandler initialize (mode="v2")
    hpob_hdlr = HPOBHandler(root_dir=root_dir, mode="v2")
    # v2 data loading
    hpob_hdlr.load_data(rootdir=root_dir, version="v2", only_test=False)
    # Get dataset IDs corresponding to search space ID
    search_space_id = str(search_space)
    dataset_ids = list(hpob_hdlr.meta_test_data[search_space_id].keys())

    all_data = pd.DataFrame()
    num_dataset = 0
    num_eval = 0

    # load data
    for dataset_id in dataset_ids:
        num_dataset += 1
        data = hpob_hdlr.meta_test_data[search_space_id][dataset_id]
        X = np.array(data['X'])
        y = np.array(data['y'])
        num_eval += len(y)
        df = pd.DataFrame(np.hstack((X, y.reshape(-1, 1))), columns=[f'X{i + 1}' for i in range(X.shape[1])] + ['y'])
        all_data = pd.concat([all_data, df])

    # round up and calculate the average y if x duplicated
    x_columns = [f'X{i + 1}' for i in range(X.shape[1])]
    for col in x_columns:
        all_data[col] = all_data[col].round(round_digits)
    grouped = all_data.groupby(x_columns, as_index=False)['y'].mean()
    grouped['y'] = grouped['y'].round(round_digits)

    all_X = grouped[x_columns].values.tolist()
    all_y = grouped['y'].tolist()
    dimension = grouped.shape[1] - 1

    if save_to_excel:
        csv_path = f"{data_num}_{dim}D.csv"
        grouped.to_csv(csv_path, index=False)
        print(f"Data saved to {csv_path}")

    print(f"Dataset: {num_dataset}")
    print(f"Eval: {num_eval}")
    print(f"New eval: {len(all_X)}")
    print(f"Dimension: {dimension}")
    print(f"Data compression rate: {(num_eval - len(all_X)) / num_eval * 100:.2f}%")

    return all_X, all_y, dimension


# Example usage
data_list = [
    [5636, 6],
    [5859, 6],
    [5906, 16],
    [7607, 9],
    [7609, 9],
]

for data_num, dim in data_list:
    print(f"\nProcessing Search Space: {data_num}")
    process_v2_data(data_num, True, round_digits=5)