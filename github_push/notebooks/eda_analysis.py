import pandas as pd
import numpy as np
import os

# Load dataset
csv_path = os.path.join("..", "data", "social_profiles_data.csv")
if not os.path.exists(csv_path):
    csv_path = "data/social_profiles_data.csv"

df = pd.read_csv(csv_path)

print(f"Total Profiles Loaded: {len(df)}")
print(df.head())

# Compute Follower-to-Following Reciprocity Ratio
df["ratio"] = df["followers"] / df["following"].replace(0, 1)

# Check distribution between Genuine and Fake accounts
if "is_fake" in df.columns or "label" in df.columns:
    label_col = "is_fake" if "is_fake" in df.columns else "label"
    print("\n--- Summary Statistics by Label ---")
    print(df.groupby(label_col)[["followers", "following", "ratio", "posts"]].median())
    
    # Calculate Separation Thresholds
    fake_df = df[df[label_col] == 1]
    real_df = df[df[label_col] == 0]
    
    print("\nRecommended Thresholds from Data:")
    print(f"Typical Fake Account Ratio: {fake_df['ratio'].median():.4f}")
    print(f"Typical Real Account Ratio: {real_df['ratio'].median():.4f}")