import os
import numpy as np
from txt2wad.wad_loader import main as load_wad

from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, f1_score

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

    user_guesses = []
    for file in files:
        load_wad(os.path.join(playtest_wads, file))

        while True:
            user_guess = input("Is this map generated? (1 = yes, 0 = no): ").strip().lower()
            if user_guess in ['1', '0']:
                user_guess = int(user_guess)
                user_guesses.append(user_guess)
                break
            else:
                print("Invalid input. Please enter 1 or 0.")

    print(f"The labels of the maps were: {labels}")




    # ground truth (1 = generated, 0 = original)
    y_true = np.array(labels)
    # User labels
    y_pred = np.array(user_guesses)

    # confusion-matrix counts
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    # derived metrics
    accuracy   = accuracy_score(y_true, y_pred)
    precision  = precision_score(y_true, y_pred, zero_division=0) 
    recall     = recall_score(y_true, y_pred)
    f1         = f1_score(y_true, y_pred)

    # display results
    print(f"TP = {tp}, FP = {fp}, TN = {tn}, FN = {fn}\n")
    print(f"Accuracy          : {accuracy:.3f}")
    print(f"Precision         : {precision:.3f}")
    print(f"Recall            : {recall:.3f}")
    print(f"F1 score          : {f1:.3f}")