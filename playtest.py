import os
import numpy as np
from txt2wad.wad_loader import main as load_wad

if __name__ == "__main__":
    np.random.seed(0)

    # Eval paths
    playtest_wads = "WFCGenerator/playtest"

    files = os.listdir(playtest_wads)
    labels = np.ones(len(files))  # 1=generated, 0=original
    for i, file in enumerate(files):
        if not file.startswith("generated"):
            labels[i] = 0

    maps = list(zip(files, labels))  # Pair the elements
    np.random.shuffle(maps)  # Shuffle the pairs
    files, labels = zip(*maps)  # Unzip into separate lists

    for file in files:
        load_wad(os.path.join(playtest_wads, file))

    print(f"The labels of the maps were: {labels}")