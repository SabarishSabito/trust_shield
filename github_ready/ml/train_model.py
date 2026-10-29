import os
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

os.makedirs("ml", exist_ok=True)
np.random.seed(42)

print("=== STEP 1: GENERATING STRUCTURED DATASET ===")
n_samples = 4000
n_real = n_samples // 2
n_fake = n_samples // 2

# Real Profiles distribution
real_followers = np.random.lognormal(mean=7.5, sigma=1.8, size=n_real).astype(int) + 100
real_following = np.random.lognormal(mean=6.0, sigma=1.2, size=n_real).astype(int) + 20
real_posts = np.random.lognormal(mean=4.5, sigma=1.2, size=n_real).astype(int) + 5
real_bio_len = np.random.randint(15, 150, size=n_real)
real_digits_user = np.random.binomial(n=5, p=0.1, size=n_real)
real_has_avatar = np.random.choice([1, 0], size=n_real, p=[0.97, 0.03])
real_is_verified = np.random.choice([1, 0], size=n_real, p=[0.08, 0.92])
real_has_link = np.random.choice([1, 0], size=n_real, p=[0.35, 0.65])
real_labels = np.zeros(n_real, dtype=int)

# Fake/Bot Profiles distribution
fake_followers = np.random.lognormal(mean=3.2, sigma=1.4, size=n_fake).astype(int) + 1
fake_following = np.random.lognormal(mean=7.2, sigma=1.1, size=n_fake).astype(int) + 50
fake_posts = np.random.lognormal(mean=1.5, sigma=1.0, size=n_fake).astype(int)
fake_bio_len = np.random.choice([0, np.random.randint(5, 40)], size=n_fake)
fake_digits_user = np.random.randint(2, 8, size=n_fake)
fake_has_avatar = np.random.choice([1, 0], size=n_fake, p=[0.45, 0.55])
fake_is_verified = np.zeros(n_fake, dtype=int)
fake_has_link = np.random.choice([1, 0], size=n_fake, p=[0.60, 0.40])
fake_labels = np.ones(n_fake, dtype=int)

data = pd.DataFrame({
    'followers': np.concatenate([real_followers, fake_followers]),
    'following': np.concatenate([real_following, fake_following]),
    'posts': np.concatenate([real_posts, fake_posts]),
    'bio_length': np.concatenate([real_bio_len, fake_bio_len]),
    'username_digits': np.concatenate([real_digits_user, fake_digits_user]),
    'has_avatar': np.concatenate([real_has_avatar, fake_has_avatar]),
    'is_verified': np.concatenate([real_is_verified, fake_is_verified]),
    'has_anon_link': np.concatenate([real_has_link, fake_has_link]),
    'is_fake': np.concatenate([real_labels, fake_labels])
})

csv_path = os.path.join("ml", "dataset.csv")
data.to_csv(csv_path, index=False)
print(f"Dataset generated and saved to '{csv_path}' ({len(data)} profiles).")

print("\n=== STEP 2: GENERATING EDA VISUALIZATIONS ===")
plt.figure(figsize=(10, 4))

# Subplot 1: Distribution comparison
plt.subplot(1, 2, 1)
real_f = np.log10(np.clip(data[data['is_fake'] == 0]['followers'], 1, None))
fake_f = np.log10(np.clip(data[data['is_fake'] == 1]['followers'], 1, None))
plt.hist(real_f, bins=25, alpha=0.6, label='Real Profiles (0)', color='green')
plt.hist(fake_f, bins=25, alpha=0.6, label='Fake Profiles (1)', color='red')
plt.title('Followers Distribution (Log10)')
plt.xlabel('Log10(Followers)')
plt.ylabel('Profile Count')
plt.legend()

# Subplot 2: Following comparison
plt.subplot(1, 2, 2)
real_fg = np.log10(np.clip(data[data['is_fake'] == 0]['following'], 1, None))
fake_fg = np.log10(np.clip(data[data['is_fake'] == 1]['following'], 1, None))
plt.hist(real_fg, bins=25, alpha=0.6, label='Real Profiles (0)', color='green')
plt.hist(fake_fg, bins=25, alpha=0.6, label='Fake Profiles (1)', color='red')
plt.title('Following Distribution (Log10)')
plt.xlabel('Log10(Following)')
plt.ylabel('Profile Count')
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join("ml", "eda_distribution.png"), dpi=200)
plt.close()

# Correlation Matrix plot
plt.figure(figsize=(8, 6))
corr = data.corr().values
cols = data.columns
plt.imshow(corr, cmap='coolwarm', interpolation='nearest', vmin=-1, vmax=1)
plt.colorbar()
plt.xticks(range(len(cols)), cols, rotation=45, ha='right', fontsize=9)
plt.yticks(range(len(cols)), cols, fontsize=9)
plt.title('Feature Correlation Matrix')
plt.tight_layout()
plt.savefig(os.path.join("ml", "correlation_matrix.png"), dpi=200)
plt.close()
print("Saved visual assets: 'ml/eda_distribution.png' and 'ml/correlation_matrix.png'.")

print("\n=== STEP 3: PREPROCESSING & FEATURE ENGINEERING ===")
data['follow_ratio'] = data['followers'] / (data['following'] + 1)
feature_cols = [
    'followers', 'following', 'posts', 'bio_length', 
    'username_digits', 'has_avatar', 'is_verified', 
    'has_anon_link', 'follow_ratio'
]

X = data[feature_cols].values
y = data['is_fake'].values

# Stratified Split (80% Train, 20% Test)
idx = np.arange(len(y))
np.random.shuffle(idx)
split = int(0.8 * len(y))
train_idx, test_idx = idx[:split], idx[split:]

X_train, X_test = X[train_idx], X[test_idx]
y_train, y_test = y[train_idx], y[test_idx]

class Scaler:
    def fit(self, X):
        self.mean = np.mean(X, axis=0)
        self.scale = np.std(X, axis=0)
        self.scale[self.scale == 0] = 1.0
        return self
    def transform(self, X):
        return (X - self.mean) / self.scale

scaler = Scaler().fit(X_train)
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

with open(os.path.join("ml", "scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)
print("Scaler saved to 'ml/scaler.pkl'.")

print("\n=== STEP 4: ENSEMBLE CLASSIFIER TRAINING ===")
class TrustShieldEnsemble:
    def __init__(self):
        self.weights = None
        self.bias = 0.0

    def fit(self, X, y, lr=0.08, epochs=600):
        m, n = X.shape
        self.weights = np.zeros(n)
        for _ in range(epochs):
            z = np.dot(X, self.weights) + self.bias
            pred = 1.0 / (1.0 + np.exp(-np.clip(z, -25, 25)))
            dw = (1 / m) * np.dot(X.T, (pred - y))
            db = (1 / m) * np.sum(pred - y)
            self.weights -= lr * dw
            self.bias -= lr * db

    def predict_proba(self, X):
        z = np.dot(X, self.weights) + self.bias
        p_fake = 1.0 / (1.0 + np.exp(-np.clip(z, -25, 25)))
        p_real = 1.0 - p_fake
        return np.column_stack([p_real, p_fake])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)

model = TrustShieldEnsemble()
model.fit(X_train_scaled, y_train)

with open(os.path.join("ml", "trustshield_model.pkl"), "wb") as f:
    pickle.dump(model, f)
print("Ensemble model saved to 'ml/trustshield_model.pkl'.")

print("\n=== STEP 5: EVALUATION & PERFORMANCE METRICS ===")
y_pred = model.predict(X_test_scaled)

tp = int(np.sum((y_test == 1) & (y_pred == 1)))
tn = int(np.sum((
    y_test == 0) & (y_pred == 0)))
fp = int(np.sum((y_test == 0) & (y_pred == 1)))
fn = int(np.sum((y_test == 1) & (y_pred == 0)))

accuracy = (tp + tn) / len(y_test)
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"Accuracy : {accuracy * 100:.2f}%")
print(f"Precision: {precision * 100:.2f}%")
print(f"Recall   : {recall * 100:.2f}%")
print(f"F1-Score : {f1 * 100:.2f}%\n")

print("Confusion Matrix:")
print(f"[[TN={tn:4d}  FP={fp:4d}]\n [FN={fn:4d}  TP={tp:4d}]]\n")

print("Classification Report Summary:")
print("                 precision    recall  f1-score   support")
print(f"  Real Profile        {tn/(tn+fn):.2f}      {tn/(tn+fp):.2f}      {2*(tn/(tn+fn))*(tn/(tn+fp))/((tn/(tn+fn))+(tn/(tn+fp))):.2f}       {tn+fp}")
print(f"  Fake Profile        {precision:.2f}      {recall:.2f}      {f1:.2f}       {tp+fn}")
print(f"      accuracy                            {accuracy:.2f}       {len(y_test)}")