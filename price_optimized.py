import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from catboost import CatBoostRegressor, Pool
from sklearn.model_selection import train_test_split
from scipy.optimize import minimize_scalar

# 예시 데이터프레임 생성 (실제 데이터로 대체 가능)
np.random.seed(42)
df = pd.DataFrame({
    '수수료율': np.random.uniform(0.01, 0.3, 500),
    '프로그램수정횟수': np.random.randint(0, 10, 500),
    '거래취소여부': np.random.choice(['Y', 'N'], 500),
    '판매자': np.random.choice(['A업체', 'B업체', 'C업체'], 500),
    '평점': np.random.uniform(1.0, 5.0, 500),
    '이용자수': np.random.randint(10, 1000, 500),
    '대분류': np.random.choice(['홈페이지', '모바일앱'], 500),
    '총금액': np.random.randint(1000, 100000, 500)
})

# 1. CatBoost로 거래량(이용자수) 예측 모델 학습
features = ['수수료율', '프로그램수정횟수', '거래취소여부', '판매자', '평점', '대분류', '총금액']
target = '이용자수'

X = df[features]
y = df[target]

cat_features = ['거래취소여부', '판매자', '대분류']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

volume_model = CatBoostRegressor(
    iterations=300,
    learning_rate=0.1,
    depth=6,
    cat_features=cat_features,
    verbose=0,
    random_seed=42
)
volume_model.fit(X_train, y_train, eval_set=(X_test, y_test), early_stopping_rounds=30)

# 2. 수수료율별 시나리오 생성
r_range = np.linspace(0.01, 0.99, 50)
base_data = {
    '프로그램수정횟수': 2,
    '거래취소여부': 'N',
    '판매자': 'A업체',
    '평점': 4.5,
    '대분류': '홈페이지',
    '총금액': 100000
}
scenario_df = pd.DataFrame([base_data] * len(r_range))
scenario_df['수수료율'] = r_range

# 3. 거래량 예측
predict_pool = Pool(data=scenario_df, cat_features=cat_features)
predicted_volume = volume_model.predict(predict_pool)

# 4. Nash 해법 최적화
P = 100000  # 평균 거래금액

def U_customer(r, V): return (1 - r) * P * V
def U_platform(r, V): return r * P * V

def negative_nash_product(r):
    if r <= r_range.min() or r >= r_range.max():
        return 1e9
    V_r = np.interp(r, r_range, predicted_volume)
    return -1 * (U_customer(r, V_r) - 1) * (U_platform(r, V_r) - 1)

result = minimize_scalar(negative_nash_product, bounds=(0.01, 0.99), method='bounded')
optimal_fee_rate = result.x

# 5. 결과 표와 시각화
Uc_list = [(1 - r) * P * v for r, v in zip(r_range, predicted_volume)]
Up_list = [r * P * v for r, v in zip(r_range, predicted_volume)]
Nash_list = [(uc - 1) * (up - 1) for uc, up in zip(Uc_list, Up_list)]

result_df = pd.DataFrame({
    '수수료율': r_range,
    '예측_이용자수': predicted_volume,
    '고객이익': Uc_list,
    '플랫폼이익': Up_list,
    'NashProduct': Nash_list
})

print(f"✅ CatBoost 기반 Nash 최적 수수료율: {optimal_fee_rate:.4f}")
print(result_df.head())

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(r_range, Uc_list, label='고객 이익', color='blue')
plt.plot(r_range, Up_list, label='플랫폼 이익', color='red')
plt.plot(r_range, Nash_list, label='Nash Product', color='green')
plt.axvline(optimal_fee_rate, color='purple', linestyle='--', label=f'최적 수수료율 = {optimal_fee_rate:.2%}')
plt.title("CatBoost 기반 수수료율 시뮬레이션")
plt.xlabel("수수료율")
plt.ylabel("이익")
plt.grid(True)
plt.legend()
plt.show()
