# 📖 Usage Guide

## 🚀 **Quick Start**

### **Step 1: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 2: Train the Model** (if not already trained)
```bash
cd train
python3 train_advanced_accuracy.py
```

This will:
- Load training data from `../data/`
- Train ensemble model
- Save models to `../models/`
- Training accuracy: **99.37%**

### **Step 3: Test the Model**
```bash
cd test
python3 test_advanced_accuracy.py
```

This will:
- Load models from `../models/`
- Test on final test data from `../data/`
- Test accuracy: **91.43%** ✅

---

## 📁 **Package Structure**

```
final_model_package/
├── train/
│   └── train_advanced_accuracy.py    # Training script
├── test/
│   └── test_advanced_accuracy.py     # Testing script
├── data/
│   ├── training_camera.csv          # Training data
│   ├── training_rcu.csv
│   ├── training_loop.csv
│   ├── test_camera_final.csv        # Test data
│   ├── test_rcu_final.csv
│   └── test_loop_final.csv
├── models/
│   ├── isolation_forest_model.joblib    # IF model
│   ├── ensemble_model.joblib            # Ensemble model
│   └── data_scaler.joblib               # Scaler
└── docs/
    ├── ACCURACY_80_PLUS_SUCCESS.md      # Success report
    ├── FINAL_IMPROVEMENT_SUMMARY.md     # Summary
    └── QUICK_REFERENCE.md               # Quick ref
```

---

## 💻 **Using the Model in Your Code**

### **Example 1: Load and Use the Model**
```python
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load models
scaler = joblib.load('models/data_scaler.joblib')
ensemble = joblib.load('models/ensemble_model.joblib')

# Load your data
# ... (your data loading code)

# Preprocess (same as training)
# ... (apply feature engineering and scaling)

# Predict
iso_scores = ensemble['iso_forest'].decision_function(X_scaled)
xgb_proba = ensemble['xgb_model'].predict_proba(X_scaled)[:, 1]

# Normalize and combine
iso_scores_norm = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min() + 1e-6)
iso_scores_norm = 1 - iso_scores_norm
combined_scores = 0.7 * iso_scores_norm + 0.3 * xgb_proba

# Predict anomalies (threshold = 0.12 percentile)
threshold = np.percentile(combined_scores, 100 * 0.12)
predictions = (combined_scores > threshold).astype(int)
```

### **Example 2: Batch Prediction**
```python
import joblib
import pandas as pd
import numpy as np

def predict_anomalies(data_path):
    """Predict anomalies for new data."""
    # Load models
    scaler = joblib.load('models/data_scaler.joblib')
    ensemble = joblib.load('models/ensemble_model.joblib')
    
    # Load data
    df = pd.read_csv(data_path)
    # ... (preprocess data)
    
    # Predict
    # ... (use code from Example 1)
    
    return predictions
```

---

## 📊 **Model Performance**

### **Training**:
- Accuracy: **99.37%**
- ROC-AUC: **0.997**
- F1-Score: **0.963**

### **Testing**:
- Accuracy: **91.43%** ✅
- ROC-AUC: **0.897**
- F1-Score: **0.921**

---

## ✅ **Checklist**

Before using the model:
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Models exist in `models/` folder
- [ ] Training data exists in `data/` folder
- [ ] Test data exists in `data/` folder

---

## 🆘 **Troubleshooting**

### **Issue: Models not found**
```bash
# Check if models exist
ls -lh models/
```

### **Issue: Data files not found**
```bash
# Check if data exists
ls -lh data/
```

### **Issue: Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

---

**Status**: ✅ Ready to use

