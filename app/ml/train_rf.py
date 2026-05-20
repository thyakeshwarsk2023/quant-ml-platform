# =========================
# EVALUATE MODEL
# =========================
from scipy.stats import spearmanr
import numpy as np
import pandas as pd
import joblib

from lightgbm import LGBMRegressor

from sklearn.metrics import mean_squared_error, r2_score

from app.ml.dataset_builder import get_training_data


MODEL_PATH = "app/ml/lgbm_model.pkl"


# =========================
# LOAD DATA
# =========================
def load_data():

    df = get_training_data()

    if df.empty:
        raise ValueError("❌ Dataset is empty")

    print(f"✅ Dataset loaded: {df.shape}")

    return df


# =========================
# PREPARE FEATURES
# =========================
def prepare_data(df):

    # 🔥 IMPORTANT: NO TARGET LEAKAGE
    features = [

        # STRATEGY FEATURES
        "sharpe",
        "max_drawdown",
        "risk_reward",
        "win_quality",
        "stability",
        "consistency",

        # MARKET FEATURES
        "mkt_volatility",
        "momentum",
        "trend_strength",
        "volume_spike",

        # ADVANCED FEATURES
        "atr",
        "macd",
        "macd_signal",
        "bb_width"
    ]

    missing = [
        f for f in features
        if f not in df.columns
    ]

    if missing:
        raise ValueError(
            f"❌ Missing features: {missing}"
        )

    X = df[features]

    # 🔥 TARGET
    y = df["target"]

    return X, y, features


# =========================
# SPLIT DATA
# =========================
def split_data(df, features):

    # =========================
    # UNIQUE SYMBOLS
    # =========================
    symbols = df["symbol"].unique()

    split_index = int(len(symbols) * 0.8)

    train_symbols = symbols[:split_index]
    test_symbols = symbols[split_index:]

    # =========================
    # SPLIT DATAFRAMES
    # =========================
    train_df = df[
        df["symbol"].isin(train_symbols)
    ]

    test_df = df[
        df["symbol"].isin(test_symbols)
    ]

    # =========================
    # FEATURES/TARGET
    # =========================
    X_train = train_df[features]
    y_train = train_df["target"]

    X_test = test_df[features]
    y_test = test_df["target"]

    print("\n📌 SYMBOL SPLIT")
    print(f"Train symbols: {len(train_symbols)}")
    print(f"Test symbols : {len(test_symbols)}")

    print(f"Train rows: {len(train_df)}")
    print(f"Test rows : {len(test_df)}")

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )
# =========================
# TRAIN MODEL
# =========================
def train_model(X_train, y_train):

    model = LGBMRegressor(

        # BOOSTING
        n_estimators=800,
        learning_rate=0.02,

        # TREE CONTROL
        max_depth=8,
        num_leaves=31,

        # REGULARIZATION
        subsample=0.8,
        colsample_bytree=0.8,

        reg_alpha=0.5,
        reg_lambda=0.5,

        # OVERFIT CONTROL
        min_child_samples=30,

        # PERFORMANCE
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    return model


# =========================
# EVALUATE MODEL
# =========================
# =========================
# EVALUATE MODEL
# =========================
from scipy.stats import spearmanr
import numpy as np


def evaluate(
    model,
    X_train,
    y_train,
    X_test,
    y_test
):

    # =========================
    # TRAIN PREDICTIONS
    # =========================
    train_preds = model.predict(X_train)

    train_r2 = r2_score(
        y_train,
        train_preds
    )

    # =========================
    # TEST PREDICTIONS
    # =========================
    preds = model.predict(X_test)

    # =========================
    # BASIC METRICS
    # =========================
    mse = mean_squared_error(
        y_test,
        preds
    )

    r2 = r2_score(
        y_test,
        preds
    )

    # =========================
    # 🔥 SPEARMAN RANK IC
    # =========================
    rank_ic, _ = spearmanr(
        y_test,
        preds
    )

    # =========================
    # 🔥 TOP-K HIT RATE
    # =========================
    top_k = max(
        1,
        int(len(preds) * 0.1)
    )

    # TOP PREDICTED
    pred_top_idx = np.argsort(
        preds
    )[-top_k:]

    # TRUE TOP
    true_top_idx = np.argsort(
        y_test.values
    )[-top_k:]

    # OVERLAP
    overlap = len(
        set(pred_top_idx)
        &
        set(true_top_idx)
    )

    hit_rate = overlap / top_k

    # =========================
    # PRINT RESULTS
    # =========================
    print("\n📊 MODEL PERFORMANCE")

    print(
        f"Train R2      : "
        f"{round(train_r2, 4)}"
    )

    print(
        f"Test R2       : "
        f"{round(r2, 4)}"
    )

    print(
        f"MSE           : "
        f"{round(mse, 6)}"
    )

    print(
        f"Rank IC       : "
        f"{round(rank_ic, 4)}"
    )

    print(
        f"Top-K HitRate : "
        f"{round(hit_rate, 4)}"
    )

    # =========================
    # RETURN
    # =========================
    return {

        "predictions":
            preds,

        "r2":
            r2,

        "rank_ic":
            rank_ic,

        "top_k_hit_rate":
            hit_rate
    }


# =========================
# FEATURE IMPORTANCE
# =========================
def show_feature_importance(
    model,
    features
):

    importance = (
        model.feature_importances_
    )

    feat_imp = pd.Series(
        importance,
        index=features
    ).sort_values(
        ascending=False
    )

    print("\n🔥 FEATURE IMPORTANCE")

    print(feat_imp)

    return feat_imp


# =========================
# SAVE MODEL
# =========================
def save_model(model):

    joblib.dump(
        model,
        MODEL_PATH
    )

    print(
        "\n✅ Model saved successfully"
    )


# =========================
# MAIN PIPELINE
# =========================
# =========================
# MAIN PIPELINE
# =========================
def train():

    # =========================
    # LOAD DATA
    # =========================
    df = load_data()

    # =========================
    # PREPARE FEATURES
    # =========================
    X, y, features = prepare_data(df)

    # =========================
    # SYMBOL SPLIT
    # =========================
    X_train, X_test, y_train, y_test = split_data(
        df,
        features
    )

    # =========================
    # TRAIN MODEL
    # =========================
    model = train_model(
        X_train,
        y_train
    )

    # =========================
    # EVALUATE
    # =========================
    metrics = evaluate(
        model,
        X_train,
        y_train,
        X_test,
        y_test
    )

    # =========================
    # FEATURE IMPORTANCE
    # =========================
    show_feature_importance(
        model,
        features
    )

    # =========================
    # SAVE MODEL
    # =========================
    save_model(model)

    # =========================
    # LEAKAGE WARNING
    # =========================
    if metrics["r2"] > 0.7:
        print(
            "\n⚠️ WARNING: "
            "Suspiciously high R2 — "
            "possible leakage"
        )

# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":

    train()

