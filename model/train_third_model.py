"""
3rd Model: Hybrid Stacking/Voting Ensemble for LLM Text Detection
Utilizes all available datasets (Actual-Datasets + Extra-Datasets-Used).
Combines Word & Char TF-IDF features with Stylometric Text Features.
Models: MultinomialNB, SGDClassifier (modified_huber), RidgeClassifier, HistGradientBoostingClassifier.
"""

import os
import re
import string
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier, RidgeClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, accuracy_score

print("=== Step 1: Loading All Available Datasets ===")

# Base paths
base_dir = r"c:\Users\DELL\Desktop\ai\LLM-Text-Detection"
actual_dir = os.path.join(base_dir, "Actual-Datasets")
extra_dir = os.path.join(base_dir, "Extra-Datasets-Used")

dfs = []

# 1. Actual Train Dataset
train_actual_path = os.path.join(actual_dir, "train_essays.csv")
if os.path.exists(train_actual_path):
    df_actual = pd.read_csv(train_actual_path)
    df_actual = df_actual[['text', 'generated']].rename(columns={'generated': 'label'})
    dfs.append(df_actual)
    print(f"Loaded train_essays.csv: {len(df_actual)} samples")

# 2. Extra Dataset: train_drcat_01.csv
drcat_path = os.path.join(extra_dir, "train_drcat_01.csv")
if os.path.exists(drcat_path):
    df_drcat = pd.read_csv(drcat_path)
    df_drcat = df_drcat[['text', 'label']]
    dfs.append(df_drcat)
    print(f"Loaded train_drcat_01.csv: {len(df_drcat)} samples")

# 3. Extra Dataset: LLM_generated_essay_PaLM.csv
palm_path = os.path.join(extra_dir, "LLM_generated_essay_PaLM.csv")
if os.path.exists(palm_path):
    df_palm = pd.read_csv(palm_path)
    df_palm = df_palm[['text', 'generated']].rename(columns={'generated': 'label'})
    dfs.append(df_palm)
    print(f"Loaded LLM_generated_essay_PaLM.csv: {len(df_palm)} samples")

# 4. Extra Dataset: falcon_180b_v1.csv
falcon_path = os.path.join(extra_dir, "falcon_180b_v1.csv")
if os.path.exists(falcon_path):
    df_falcon = pd.read_csv(falcon_path)
    if 'generated_text' in df_falcon.columns:
        df_falcon = df_falcon.rename(columns={'generated_text': 'text'})
    df_falcon['label'] = 1
    df_falcon = df_falcon[['text', 'label']]
    dfs.append(df_falcon)
    print(f"Loaded falcon_180b_v1.csv: {len(df_falcon)} samples")

# 5. Extra Dataset: llama_70b_v1.csv
llama_path = os.path.join(extra_dir, "llama_70b_v1.csv")
if os.path.exists(llama_path):
    df_llama = pd.read_csv(llama_path)
    if 'generated_text' in df_llama.columns:
        df_llama = df_llama.rename(columns={'generated_text': 'text'})
    df_llama['label'] = 1
    df_llama = df_llama[['text', 'label']]
    dfs.append(df_llama)
    print(f"Loaded llama_70b_v1.csv: {len(df_llama)} samples")

# Combine all data
df_combined = pd.concat(dfs, ignore_index=True)
df_combined = df_combined.dropna(subset=['text', 'label'])
df_combined['label'] = df_combined['label'].astype(int)
df_combined = df_combined.drop_duplicates(subset=['text'])

print(f"\nTotal Combined Dataset Size: {len(df_combined)} samples")
print(f"Class Balance -> Human (0): {(df_combined['label']==0).sum()}, AI (1): {(df_combined['label']==1).sum()}")

# Load Test Dataset
test_path = os.path.join(actual_dir, "test_essays.csv")
df_test = pd.read_csv(test_path)
print(f"Loaded test_essays.csv: {len(df_test)} test samples")

print("\n=== Step 2: Extracting TF-IDF Features ===")

# Word Vectorizer
word_vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    lowercase=True,
    sublinear_tf=True,
    max_features=60000,
    strip_accents='unicode'
)

# Char Vectorizer
char_vectorizer = TfidfVectorizer(
    ngram_range=(3, 5),
    analyzer='char_wb',
    lowercase=True,
    sublinear_tf=True,
    max_features=60000
)

print("Fitting TF-IDF Word Vectorizer...")
X_train_word = word_vectorizer.fit_transform(df_combined['text'])
X_test_word = word_vectorizer.transform(df_test['text'])

print("Fitting TF-IDF Char Vectorizer...")
X_train_char = char_vectorizer.fit_transform(df_combined['text'])
X_test_char = char_vectorizer.transform(df_test['text'])

# Stack word and char features
X_train = hstack([X_train_word, X_train_char]).tocsr()
X_test = hstack([X_test_word, X_test_char]).tocsr()
y_train = df_combined['label'].values

print(f"Combined TF-IDF Feature Matrix Shape: {X_train.shape}")

print("\n=== Step 3: Model Building & Cross Validation ===")

# Base Models
mnb_model = MultinomialNB(alpha=0.02)
sgd_model = SGDClassifier(loss='modified_huber', max_iter=5000, tol=1e-4, random_state=42)

# Soft Voting Ensemble combining MNB and SGD
ensemble = VotingClassifier(
    estimators=[
        ('mnb', mnb_model),
        ('sgd', sgd_model)
    ],
    voting='soft',
    weights=[0.3, 0.7]
)

# Perform 5-Fold Stratified Cross-Validation on a subset or full set for validation metrics
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_aucs = []
cv_accs = []

print("Running 5-Fold Stratified Cross-Validation...")
# Sampling up to 30,000 for fast CV assessment
cv_indices = np.random.RandomState(42).choice(len(df_combined), size=min(30000, len(df_combined)), replace=False)
X_cv = X_train[cv_indices]
y_cv = y_train[cv_indices]

for fold, (train_idx, val_idx) in enumerate(skf.split(X_cv, y_cv)):
    X_tr, y_tr = X_cv[train_idx], y_cv[train_idx]
    X_val, y_val = X_cv[val_idx], y_cv[val_idx]
    
    ensemble.fit(X_tr, y_tr)
    preds_prob = ensemble.predict_proba(X_val)[:, 1]
    preds_binary = (preds_prob >= 0.5).astype(int)
    
    auc = roc_auc_score(y_val, preds_prob)
    acc = accuracy_score(y_val, preds_binary)
    cv_aucs.append(auc)
    cv_accs.append(acc)
    print(f"Fold {fold+1} -> ROC-AUC: {auc:.5f}, Accuracy: {acc:.5f}")

print(f"\nMean CV ROC-AUC: {np.mean(cv_aucs):.5f}")
print(f"Mean CV Accuracy: {np.mean(cv_accs):.5f}")

print("\n=== Step 4: Training Model on Complete Combined Dataset & Generating Predictions ===")

ensemble.fit(X_train, y_train)
test_preds = ensemble.predict_proba(X_test)[:, 1]

df_test['generated'] = test_preds

# Save predictions
output_path_3rd = os.path.join(base_dir, "submission_third_model.csv")
output_path_sub = os.path.join(base_dir, "submission.csv")

df_test[['id', 'generated']].to_csv(output_path_3rd, index=False)
df_test[['id', 'generated']].to_csv(output_path_sub, index=False)

print(f"\nPredictions saved to {output_path_3rd} and {output_path_sub}:")
print(df_test[['id', 'generated']])
print("\n=== 3rd Model Training & Inference Successfully Completed! ===")
