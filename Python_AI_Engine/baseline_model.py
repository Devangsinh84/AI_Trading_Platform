import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os

class BaselineModel:
    def __init__(self, train_path, test_path, model_output_path):
        self.train_path = train_path
        self.test_path = test_path
        self.model_output_path = model_output_path
        
        # Initialize the XGBoost Classifier
        # These parameters are a standard starting point for financial time-series
        self.model = xgb.XGBClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            eval_metric='logloss'
        )

    def load_data(self):
        print(f"[*] Loading datasets from {self.train_path} and {self.test_path}...")
        train_df = pd.read_csv(self.train_path, index_col='Date', parse_dates=True)
        test_df = pd.read_csv(self.test_path, index_col='Date', parse_dates=True)

        # Separate Features (X) from Target (y)
        self.X_train = train_df.drop(columns=['Target'])
        self.y_train = train_df['Target']

        self.X_test = test_df.drop(columns=['Target'])
        self.y_test = test_df['Target']
        print(f"[+] Data loaded successfully. Training samples: {len(self.X_train)}, Testing samples: {len(self.X_test)}")

    def train(self):
        print("[*] Training the XGBoost Baseline Model...")
        self.model.fit(self.X_train, self.y_train)
        print("[+] Training complete.")

    def evaluate(self):
        print("[*] Evaluating model performance on unseen test data...")
        predictions = self.model.predict(self.X_test)
        
        # Calculate institutional metrics
        acc = accuracy_score(self.y_test, predictions)
        prec = precision_score(self.y_test, predictions)
        rec = recall_score(self.y_test, predictions)
        f1 = f1_score(self.y_test, predictions)

        print("\n==========================================")
        print("BASELINE MODEL RESULTS (XGBoost)")
        print("==========================================")
        print(f"Accuracy:  {acc:.4f}")
        print(f"Precision: {prec:.4f}  <-- Crucial for minimizing false positive trades")
        print(f"Recall:    {rec:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        print("==========================================\n")

    def save_model(self):
        joblib.dump(self.model, self.model_output_path)
        print(f"[+] Model successfully saved to {self.model_output_path}")

# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    train_csv = os.path.join("data", "SP500_train.csv")
    test_csv = os.path.join("data", "SP500_test.csv")
    model_out = os.path.join("data", "xgboost_baseline.pkl")
    
    try:
        baseline = BaselineModel(train_csv, test_csv, model_out)
        baseline.load_data()
        baseline.train()
        baseline.evaluate()
        baseline.save_model()
        
        print("\n[SUCCESS] Task 2.3 Baseline AI Model Training is complete.")
        
    except Exception as e:
        print(f"\n[ERROR] Baseline training failed: {e}")