import numpy as np
import pandas as pd

np.random.seed(42)
n_samples = 1000

labels = np.random.choice([0, 1], size=n_samples, p=[0.55, 0.45])

data = {
    "profile_id": [f"USR_{1000 + i}" for i in range(n_samples)],
    "account_age_days": np.where(labels == 1, np.random.randint(1, 45, n_samples), np.random.randint(60, 1800, n_samples)),
    "followers_count": np.where(labels == 1, np.random.randint(0, 150, n_samples), np.random.randint(100, 5000, n_samples)),
    "following_count": np.where(labels == 1, np.random.randint(500, 4000, n_samples), np.random.randint(50, 800, n_samples)),
    "posts_count": np.where(labels == 1, np.random.randint(0, 5, n_samples), np.random.randint(20, 400, n_samples)),
    "messages_per_hr": np.where(labels == 1, np.random.uniform(20.0, 90.0, n_samples), np.random.uniform(0.1, 8.0, n_samples)),
    "bio_has_spam_keywords": np.where(labels == 1, np.random.choice([1, 0], n_samples, p=[0.75, 0.25]), np.random.choice([1, 0], n_samples, p=[0.05, 0.95])),
    "has_profile_pic": np.where(labels == 1, np.random.choice([1, 0], n_samples, p=[0.40, 0.60]), np.random.choice([1, 0], n_samples, p=[0.95, 0.05])),
    "is_fake": labels
}

df = pd.DataFrame(data)
df.loc[np.random.choice(df.index, size=25), 'account_age_days'] = np.nan
df.to_csv("data/social_profiles_dataset.csv", index=False)
print("SUCCESS: Dataset saved to data/social_profiles_dataset.csv")