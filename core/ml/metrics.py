import numpy as np
import pandas as pd
from sklearn.metrics import (
    roc_auc_score,
    roc_curve,
    accuracy_score,
    precision_score,
    f1_score,
    recall_score,
    log_loss,
)



def metrics_classification(y, y_score):
    """
    Parameters
    ----------
    y : ndarray of shape (n_samples,)
        True binary labels. If labels are not either {-1, 1} or {0, 1}, then
        pos_label should be explicitly given.

    y_score : ndarray of shape (n_samples,)
        Target scores, can either be probability estimates of the positive
        class, confidence values, or non-thresholded measure of decisions
        (as returned by "decision_function" on some classifiers).
    :return: ACC, F1, Precision, Recall, logLoss, AUC
    """
    report = {}
    if isinstance(y, pd.Series):
        y = np.array(y)
    if isinstance(y_score, pd.Series):
        y_score = np.array(y_score)
    # fpr, tpr, thresholds = roc_curve(y, y_score)
    report["auc"] = roc_auc_score(y, y_score)
    report["logLoss"] = log_loss(y, y_score)

    def prob_to_output(prob):
        if prob >= 0.5:
            return 1
        return 0
    
    y_score = np.vectorize(prob_to_output)(y_score)
    report["acc"] = accuracy_score(y, y_score)
    report["f1"] = f1_score(y, y_score)

    report["precision"] = precision_score(y, y_score) 
    report["recall"] = recall_score(y, np.round(y_score))


    return report


if __name__ == "__main__":
    y = np.array([1,0.0,0,0,1])
    y_pred = np.array([1.0,1,0,0,0])
    y_score = np.array([0.8, 0.7455, 0.32, 0.44, 0.123])
    print(metrics_classification(y, y_score))