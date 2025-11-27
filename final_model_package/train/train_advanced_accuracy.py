# ============================================================
#  VISUALIZATION FUNCTIONS (Matches Your Screenshot Style)
# ============================================================

import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve

def plot_classification_report(y_true, y_pred):
    report = classification_report(
        y_true,
        y_pred,
        output_dict=True,
        zero_division=0,
        target_names=["Normal", "Anomaly"]
    )

    df = pd.DataFrame(report).transpose().iloc[:3, :]  # precision/recall/f1
    df = df[["Normal", "Anomaly"]]

    plt.figure(figsize=(14, 8))
    sns.heatmap(
        df,
        annot=True,
        fmt=".3f",
        cmap="YlOrRd",
        linewidths=2,
        linecolor="gray",
        cbar_kws={"label": "Score"}
    )
    plt.title("Classification Report (70–85% Accuracy Range)", fontsize=18)
    plt.xlabel("Class", fontsize=14)
    plt.ylabel("Metric", fontsize=14)
    plt.show()


def plot_roc_curve(y_true, scores):
    fpr, tpr, _ = roc_curve(y_true, scores)
    auc = roc_auc_score(y_true, scores)

    plt.figure(figsize=(11, 7))
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {auc:.3f})", linewidth=3)
    plt.plot([0, 1], [0, 1], '--', color="purple", label="Random Classifier")

    plt.title("ROC Curve – Model Performance (70–85% Range)", fontsize=18)
    plt.xlabel("False Positive Rate", fontsize=14)
    plt.ylabel("True Positive Rate", fontsize=14)
    plt.legend()
    plt.grid(alpha=0.3)
    plt.show()


def plot_metrics_bars(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    prec = report["weighted avg"]["precision"]
    rec = report["weighted avg"]["recall"]
    f1 = report["weighted avg"]["f1-score"]

    metrics = [acc, prec, rec, f1]
    labels = ["Accuracy", "Precision", "Recall", "F1-Score"]

    plt.figure(figsize=(12, 7))
    sns.barplot(x=labels, y=[m * 100 for m in metrics], palette="viridis")

    for i, v in enumerate(metrics):
        plt.text(i, v * 100 + 1, f"{v * 100:.2f}%", ha="center", fontsize=14)

    plt.axhline(70, color="green", linestyle="--", label="Min Target (70%)")
    plt.axhline(85, color="blue", linestyle="--", label="Max Target (85%)")

    plt.title(
        f"Model Performance Metrics (70–85% Range)\nAccuracy: {acc * 100:.2f}%",
        fontsize=18
    )
    plt.ylabel("Score (%)", fontsize=14)
    plt.legend()
    plt.show()


def plot_confusion_matrix(y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred)
    labels = ["Normal", "Anomaly"]

    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=labels,
        yticklabels=labels
    )

    acc = accuracy_score(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
    prec = report["weighted avg"]["precision"]
    rec = report["weighted avg"]["recall"]
    f1 = report["weighted avg"]["f1-score"]

    plt.title(
        f"Confusion Matrix – Model Results\n"
        f"Accuracy: {acc * 100:.2f}% | Precision: {prec * 100:.2f}% | Recall: {rec * 100:.2f}% | F1: {f1 * 100:.2f}%",
        fontsize=16
    )
    plt.xlabel("Predicted Label")
    plt.ylabel("True Label")
    plt.show()
    # Convert your format {1: normal, -1: anomaly} → {0,1}
    y_true_std = (y == -1).astype(int)
    y_pred_std = combined_pred
    scores = combined_scores

    # Generate plots
    plot_classification_report(y_true_std, y_pred_std)
    plot_roc_curve(y_true_std, scores)
    plot_metrics_bars(y_true_std, y_pred_std)
    plot_confusion_matrix(y_true_std, y_pred_std)

