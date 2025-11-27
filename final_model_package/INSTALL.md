# 📦 Installation Guide

## 🔧 **Setup Instructions**

### **1. Install Python Dependencies**:
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pandas numpy scikit-learn xgboost matplotlib seaborn joblib
```

### **2. Verify Installation**:
```bash
python3 -c "import pandas, numpy, sklearn, xgboost, matplotlib, seaborn, joblib; print('All packages installed successfully!')"
```

### **3. Check File Structure**:
```bash
ls -R
```

You should see:
- `train/` - Training scripts
- `test/` - Testing scripts
- `data/` - Data files
- `models/` - Model files
- `docs/` - Documentation

---

## 🚀 **Quick Test**

### **Test if models are ready**:
```bash
python3 -c "import joblib; print('Models:', joblib.load('models/isolation_forest_model.joblib')); print('✅ Models loaded successfully!')"
```

---

## ✅ **Ready to Use**

Once installed, you can:
1. Train: `cd train && python3 train_advanced_accuracy.py`
2. Test: `cd test && python3 test_advanced_accuracy.py`

---

**Status**: ✅ Ready for use

