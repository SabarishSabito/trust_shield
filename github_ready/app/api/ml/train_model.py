import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import joblib

os.makedirs("ml", exist_ok=True)
np.random.seed(42)

print("=== STEP 1: GENERATING DATASET ===")
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
print(f"Dataset saved to '{csv_path}' ({len(data)} rows).")

print("\n=== STEP 2: GENERATING EDA PLOTS ===")
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
sns.boxplot(x='is_fake', y='followers', data=data, palette='Set2')
plt.yscale('log')
plt.title('Followers Count (Log Scale)')
plt.xlabel('Class (0: Real, 1: Fake)')

plt.subplot(1, 2, 2)
sns.boxplot(x='is_fake', y='following', data=data, palette='Set2')
plt.yscale('log')
plt.title('Following Count (Log Scale)')
plt.xlabel('Class (0: Real, 1: Fake)')
plt.tight_layout()
plt.savefig(os.path.join("ml", "eda_distribution.png"), dpi=200)
plt.close()

plt.figure(figsize=(8, 6))
sns.heatmap(data.corr(), annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
plt.title('Feature Correlation Matrix with Fake Profiles')
plt.tight_layout()
plt.savefig(os.path.join("ml", "correlation_matrix.png"), dpi=200)
plt.close()
print("Saved plots: 'ml/eda_distribution.png' and 'ml/correlation_matrix.png'.")

print("\n=== STEP 3: PREPROCESSING & SCALING ===")
data['follow_ratio'] = data['followers'] / (data['following'] + 1)
feature_cols = [
    'followers', 'following', 'posts', 'bio_length', 
    'username_digits', 'has_avatar', 'is_verified', 
    'has_anon_link', 'follow_ratio'
]

X = data[feature_cols]
y = data['is_fake']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

joblib.dump(scaler, os.path.join("ml", "scaler.pkl"))
print("Scaler saved to 'ml/scaler.pkl'.")

print("\n=== STEP 4: TRAINING ENSEMBLE MODEL ===")
iso_forest = IsolationForest(contamination=0.1, random_state=42)
iso_forest.fit(X_train_scaled)

rf_clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
gb_clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42)

ensemble_model = VotingClassifier(
    estimators=[('rf', rf_clf), ('gb', gb_clf)],
    voting='soft'
)
ensemble_model.fit(X_train_scaled, y_train)

joblib.dump(ensemble_model, os.path.join("ml", "trustshield_model.pkl"))
print("Ensemble model saved to 'ml/trustshield_model.pkl'.")

print("\n=== STEP 5: EVALUATION METRICS ===")
y_pred = ensemble_model.predict(X_test_scaled)
print(f"Accuracy : {accuracy_score(y_test, y_pred) * 100:.2f}%")
print(f"Precision: {precision_score(y_test, y_pred) * 100:.2f}%")
print(f"Recall   : {recall_score(y_test, y_pred) * 100:.2f}%")
print(f"F1-Score : {f1_score(y_test, y_pred) * 100:.2f}%\n")
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Real Profile", "Fake Profile"]))