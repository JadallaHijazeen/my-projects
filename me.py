from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model, metrics
from sklearn.preprocessing import MinMaxScaler

data = pd.read_csv("StudentsPerformance.csv")

print(data.head(10))
print(data.shape)
print(data.columns)
print(data.info())
print(data.describe())

print("Show the nubmer of null values\n---------------------------- ")
print(data.isnull().sum())
data = data.dropna()

data = data.drop_duplicates()
print(data.info())

print("======================================================")
print(" Outlier Data ")
print("======================================================")
Q1 = data['math score'].quantile(0.25)
Q3 = data['math score'].quantile(0.75)
IQR = Q3 - Q1
print("Q1=", Q1)
print("Q3=", Q3)
print("IQR=", IQR)
Lower_Whisker = Q1 - 1.5 * IQR
Upper_Whisker = Q3 + 1.5 * IQR
print(Lower_Whisker, Upper_Whisker)
data = data[data['math score'] < Upper_Whisker]
print(data.info())

plt.scatter(data["reading score"], data["math score"])
plt.title("Math score vs Reading score")
plt.xlabel("Reading score")
plt.ylabel("Math score")
plt.show()

df = data.copy()

mms = MinMaxScaler()
df["reading score"] = mms.fit_transform(df[["reading score"]])
df["writing score"] = mms.fit_transform(df[["writing score"]])

df = pd.concat([df.drop("gender", axis=1), pd.get_dummies(df["gender"], prefix="gender")], axis=1)
df = pd.concat([df.drop("race/ethnicity", axis=1), pd.get_dummies(df["race/ethnicity"], prefix="race")], axis=1)
df = pd.concat([df.drop("parental level of education", axis=1), pd.get_dummies(df["parental level of education"], prefix="parent_edu")], axis=1)
df = pd.concat([df.drop("lunch", axis=1), pd.get_dummies(df["lunch"], prefix="lunch")], axis=1)
df = pd.concat([df.drop("test preparation course", axis=1), pd.get_dummies(df["test preparation course"], prefix="prep")], axis=1)

X = df.drop(["math score"], axis=1)
y = df["math score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

reg = linear_model.LinearRegression()
reg.fit(X_train, y_train)

print('Coefficients: ', reg.coef_)
print('Variance score: {}'.format(reg.score(X_test, y_test)))

plt.style.use('fivethirtyeight')
plt.scatter(reg.predict(X_train), reg.predict(X_train) - y_train, color="green", s=10, label='Train data')
plt.scatter(reg.predict(X_test), reg.predict(X_test) - y_test, color="blue", s=10, label='Test data')
plt.hlines(y=0, xmin=0, xmax=100, linewidth=2)
plt.legend(loc='upper right')
plt.title("Residual errors")
plt.show()

mae = metrics.mean_absolute_error(y_test, reg.predict(X_test))
mse = metrics.mean_squared_error(y_test, reg.predict(X_test))
rmse = np.sqrt(mse)
r2 = metrics.r2_score(y_test, reg.predict(X_test))
print("Results of sklearn.metrics:")
print("MAE:", mae)
print("MSE:", mse)
print("RMSE:", rmse)
print("R-Squared:", r2)

X2 = data[["reading score", "writing score"]]
y2 = data["math score"]
X_train2, X_test2, y_train2, y_test2 = train_test_split(X2, y2, test_size=0.2, random_state=1)

reg2 = linear_model.LinearRegression()
reg2.fit(X_train2, y_train2)

mae2 = metrics.mean_absolute_error(y_test2, reg2.predict(X_test2))
mse2 = metrics.mean_squared_error(y_test2, reg2.predict(X_test2))
rmse2 = np.sqrt(mse2)
r2_2 = metrics.r2_score(y_test2, reg2.predict(X_test2))
print("Model 2 (only reading+writing) Results:")
print("MAE:", mae2)
print("MSE:", mse2)
print("RMSE:", rmse2)
print("R-Squared:", r2_2)
