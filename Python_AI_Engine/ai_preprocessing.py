import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import os

class AIDataPreprocessor:
    def __init__(self, input_file, output_train, output_test):
        self.input_file = input_file
        self.output_train = output_train
        self.output_test = output_test
        self.scaler = MinMaxScaler()

    def process_data(self):
        print(f"[*] Loading raw dataset from {self.input_file}...")
        # Load the CSV and tell Pandas that the 'Date' column is our timeline index
        df = pd.read_csv(self.input_file, index_col='Date', parse_dates=True)
        
        # ---------------------------------------------------------
        # PHASE 1: Define the Target (The Answer Key)
        # ---------------------------------------------------------
        print("[*] Engineering the Target Variable (Classification: 1=Up, 0=Down)...")
        # .shift(-1) looks at TOMORROW'S close. If tomorrow > today, Target is 1. Else 0.
        df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
        
        # The very last day in our dataset doesn't have a "tomorrow" yet, so we drop it.
        df.dropna(inplace=True)

        # ---------------------------------------------------------
        # PHASE 2: Separate and Scale (Leveling the Playing Field)
        # ---------------------------------------------------------
        y = df['Target'] # The Answers
        X = df.drop(columns=['Target']) # The Math (RSI, MACD, etc.)

        print("[*] Normalizing feature data with MinMaxScaler...")
        # Squish all indicator values between 0 and 1 so the AI treats them equally
        X_scaled = pd.DataFrame(self.scaler.fit_transform(X), columns=X.columns, index=X.index)

        # ---------------------------------------------------------
        # PHASE 3: The Time Machine Split
        # ---------------------------------------------------------
        print("[*] Splitting timeline into Training (80%) and Testing (20%) sets...")
        split_idx = int(len(X_scaled) * 0.8)
        
        # Past 8 years (The AI uses this to learn)
        X_train = X_scaled.iloc[:split_idx]
        y_train = y.iloc[:split_idx]
        
        # Future 2 years (The AI uses this to take its final exam)
        X_test = X_scaled.iloc[split_idx:]
        y_test = y.iloc[split_idx:]

        # ---------------------------------------------------------
        # PHASE 4: Save the AI-Ready Datasets
        # ---------------------------------------------------------
        train_df = pd.concat([X_train, y_train], axis=1)
        test_df = pd.concat([X_test, y_test], axis=1)

        train_df.to_csv(self.output_train)
        test_df.to_csv(self.output_test)
        
        print(f"[+] Training Set: {len(train_df)} days (Saved to {self.output_train})")
        print(f"[+] Testing Set: {len(test_df)} days (Saved to {self.output_test})")
        print("\n[SUCCESS] Task 2.2 Data Preprocessing is complete.")

# ==========================================
# Execution Block
# ==========================================
if __name__ == "__main__":
    # Point the engine to our saved data from Task 2.1 the csv file
    input_path = os.path.join("data", "SP500_10yr_processed.csv")
    train_path = os.path.join("data", "SP500_train.csv")
    test_path = os.path.join("data", "SP500_test.csv")
    
    try:
        preprocessor = AIDataPreprocessor(input_path, train_path, test_path)
        preprocessor.process_data()
    except Exception as e:
        print(f"\n[ERROR] Preprocessing failed: {e}")