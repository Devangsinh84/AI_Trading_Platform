import pandas as pd
import matplotlib.pyplot as plt
from stable_baselines3 import PPO

# Import the custom environment you built in Task 3.1
from trading_env import StockTradingEnv

if __name__ == "__main__":
    print("[*] Loading UNSEEN Test Dataset (The Final Exam)...")
    # Make sure we load the test data, not the train data!
    df_test = pd.read_csv("data/SP500_test.csv")
    
    print("[*] Initializing Test Environment...")
    env = StockTradingEnv(df_test)
    obs, info = env.reset()
    
    print("[*] Loading Trained PPO Brain...")
    # Load the zip file we generated in Task 3.2
    model = PPO.load("models/ppo_trading_agent")
    
    terminated = False
    net_worths = [10000] # Track portfolio over time
    actions = []
    
    print("[*] Simulating live trading on test data...")
    
    while not terminated:
        # Tell the model to predict the best action based on today's indicators.
        # HACK: Set deterministic=False to force the AI to trust its "gut" and make dynamic trades!
        action, _states = model.predict(obs, deterministic=False)
        
        # Take the action in the environment
        obs, reward, terminated, truncated, info = env.step(action)
        
        # Record the results
        net_worths.append(info["net_worth"])
        actions.append(action)

    # Calculate Final Performance Metrics
    final_worth = net_worths[-1]
    total_return = ((final_worth - 10000) / 10000) * 100
    buy_count = actions.count(1)
    cash_count = actions.count(0)
    
    print("\n=============================================")
    print("           MODEL EVALUATION REPORT           ")
    print("=============================================")
    print(f"Initial Portfolio Value : $10,000.00")
    print(f"Final Portfolio Value   : ${final_worth:.2f}")
    print(f"Total Strategy Return   : {total_return:.2f}%")
    print(f"Total Trading Days      : {len(actions)}")
    print(f"Days Invested (Action 1): {buy_count}")
    print(f"Days in Cash (Action 0) : {cash_count}")
    print("=============================================")

    # Generate the DRL Evaluation Chart
    print("\n[*] Generating Portfolio Evaluation Chart...")
    plt.figure(figsize=(10, 6))
    
    # Plot the AI's portfolio performance
    plt.plot(net_worths, label='PPO Agent Portfolio Value', color='blue', linewidth=2)
    
    # Draw a red dashed line to represent the starting balance
    plt.axhline(y=10000, color='red', linestyle='--', label='Initial Capital ($10,000)')
    
    plt.title('Deep Reinforcement Learning: PPO Agent Test Performance')
    plt.xlabel('Trading Days (Test Period)')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Save the plot for the thesis presentation
    chart_filename = "evaluation_chart.png"
    plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
    print(f"[+] Evaluation chart successfully saved as '{chart_filename}'")