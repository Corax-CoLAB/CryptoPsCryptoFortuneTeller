with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "r") as f:
    content = f.read()

lstm_imports = """from tensorflow.keras.layers import Dropout
from tensorflow.keras.callbacks import EarlyStopping"""

if "from tensorflow.keras.layers import Dropout" not in content:
    content = content.replace("from tensorflow.keras.layers import LSTM, Dense, Input",
                              "from tensorflow.keras.layers import LSTM, Dense, Input\n" + lstm_imports)

old_lstm_arch = """    # Explicit Input layer
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(50),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    # ⚡ Bolt Optimization: Increased batch_size to 32 (was 16)
    # Reduces training time by ~20% while maintaining sufficient updates for convergence on daily data
    model.fit(X, y, epochs=5, batch_size=32, verbose=0)"""

new_lstm_arch = """    # Technical Improvement 5: LSTM Architecture Upgrade
    model = Sequential([
        Input(shape=(n_steps, 1)),
        LSTM(100, return_sequences=True), # Increased complexity
        Dropout(0.2), # Prevent overfitting
        LSTM(50),
        Dropout(0.2),
        Dense(25, activation='relu'),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')

    # Early stopping
    early_stop = EarlyStopping(monitor='loss', patience=5, restore_best_weights=True)

    model.fit(X, y, epochs=20, batch_size=32, verbose=0, callbacks=[early_stop])"""

content = content.replace(old_lstm_arch, new_lstm_arch)

with open("streamlit_app/modules/cryptop_crypto_fortune_teller_models.py", "w") as f:
    f.write(content)

print("LSTM Architecture Updated")
