import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('weatherIncluded3.csv')

# Convert Race Time from string to total seconds
df['Race Time (seconds)'] = pd.to_timedelta(df['Race Time']).dt.total_seconds()

df = df.drop('Race Time', axis=1)

df['Race Time (seconds)'].fillna(-1, inplace=True)


df.isna().any()[lambda x: x]
df['Driver Name'].fillna(-1, inplace=True)
df['Position'].fillna(-1, inplace=True)
df['Race Point'].fillna(0, inplace=True)
df['Race Grid Position'].fillna(-1, inplace=True)

# Function to adjust race times while leaving DNFs untouched
def adjust_race_times_seconds(group):
    # Check if there's a first-place finisher in this group
    if (group['Position'] == 1).any():
        # Find the race time of the first-place finisher
        first_place_time = group.loc[group['Position'] == 1, 'Race Time (seconds)'].values[0]
        
        # For all other drivers, add first-place time only if they didn't DNF
        group.loc[(group['Position'] != 1) & (group['Race Time (seconds)'] != -1), 'Adjusted Race Time (seconds)'] = (
            group['Race Time (seconds)'] + first_place_time
        )
        
        # Keep first-place time as it is
        group.loc[group['Position'] == 1, 'Adjusted Race Time (seconds)'] = first_place_time
        
        # Keep DNF times (-1) unchanged
        group.loc[group['Race Time (seconds)'] == -1, 'Adjusted Race Time (seconds)'] = -1
        
    return group

# Reset index to avoid ambiguity and group by 'Race Name'
df = df.reset_index(drop=True)

# Apply the function, grouping by Race Name
df = df.groupby('Race Name', as_index=False).apply(adjust_race_times_seconds)

# Display the adjusted dataframe
print(df[['Race Name', 'Driver Name', 'Position', 'Race Time (seconds)', 'Adjusted Race Time (seconds)']])

df['Adjusted Race Time (seconds)'].fillna(-1, inplace=True)

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Clustering Features
clustering_features = ['Race Point', 'Adjusted Race Time (seconds)', 'Position', 'Race Grid Position']

# Prepare the data for clustering (normalization is important)
X_clustering = df[clustering_features]

# Normalize the data
scaler = StandardScaler()
X_clustering_scaled = scaler.fit_transform(X_clustering)

# Train the KMeans clustering model
kmeans = KMeans(n_clusters=3, random_state=10)
df['Cluster'] = kmeans.fit_predict(X_clustering_scaled)

# Visualize clusters based on driver performance
plt.figure(figsize=(10, 6))

# Scatter plot with clustering results
sns.scatterplot(
    x='Race Point', 
    y='Adjusted Race Time (seconds)', 
    hue='Cluster', 
    palette='Set2', 
    data=df, 
    s=100, 
    legend='full'
)

# Add driver names next to their dots
for i in range(len(df)):
    plt.text(
        df['Race Point'].iloc[i], 
        df['Adjusted Race Time (seconds)'].iloc[i], 
        df['Driver ID'].iloc[i], 
        fontsize=6, 
        ha='right'
    )

# Plot titles and labels
plt.title('Driver Clustering Based on Performance')
plt.xlabel('Race Point')
plt.ylabel('Race Time (seconds)')
plt.legend(title='Cluster')
plt.tight_layout()
plt.show()


# Extract the year from the Race Date column
df['Race Year'] = pd.to_datetime(df['Race Date']).dt.year

# Filter for drivers present in 2024
drivers_2024 = df[df['Race Year'] == 2024]['Driver Name'].unique()

# Filter the entire dataset to include only those drivers
df_2024_drivers = df[df['Driver Name'].isin(drivers_2024)]

# Filter for rainy races
rainy_races_2024_drivers = df_2024_drivers[df_2024_drivers['Rainfall'] == True]

# Set up the plotting environment
plt.figure(figsize=(12, 8))

# Scatter plot to visualize driver performance in rainy races (only 2024 drivers)
sns.scatterplot(
    data=rainy_races_2024_drivers,
    x='Position',
    y='Adjusted Race Time (seconds)',
    hue='Driver Name',
    size='Race Point',
    palette=sns.color_palette('husl', len(drivers_2024)),
    sizes=(100, 400),
    legend='brief'
)

# Customize the plot
plt.title('Driver Performances in Rainy Races (2024 Drivers Only)')
plt.xlabel('Position (lower is better)')
plt.ylabel('Adjusted Race Time (seconds)')
plt.legend(title='Driver')
plt.grid(True)

plt.legend(title='Driver', bbox_to_anchor=(1.05, 1), loc='upper left')

# Show the plot
plt.show()


from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Convert Race Date to datetime and extract year
df['Race Year'] = pd.to_datetime(df['Race Date']).dt.year

#  Filter for drivers present in 2024
drivers_2024 = df[df['Race Year'] == 2024]['Driver Name'].unique()

# Filter the entire dataset to include only those drivers
df_2024_drivers = df[df['Driver Name'].isin(drivers_2024)]

# Filter for wet races and 2024 drivers
wet_races = df_2024_drivers[(df_2024_drivers['Rainfall'] == True)]

# Feature Engineering
# Driver Experience: Number of races before 2024
driver_experience = df_2024_drivers[df_2024_drivers['Race Year'] < 2024].groupby('Driver Name').size().reset_index(name='Races Before 2024')
wet_races = wet_races.merge(driver_experience, on='Driver Name', how='left')
wet_races['Races Before 2024'] = wet_races['Races Before 2024'].fillna(0)

# Team Strength: Average points per race for the team
team_strength = df_2024_drivers.groupby('Driver Team')['Race Point'].mean().reset_index(name='Team Avg Points')
wet_races = wet_races.merge(team_strength, on='Driver Team', how='left')

# Historical Performance in Wet Races: Average Position
historical_wet_perf = wet_races.groupby('Driver Name')['Position'].mean().reset_index(name='Avg Finishing Pos Wet')
wet_races = wet_races.merge(historical_wet_perf, on='Driver Name', how='left')
wet_races['Avg Finishing Pos Wet'] = wet_races['Avg Finishing Pos Wet'].fillna(wet_races['Position'].mean())

# Encoding Categorical Variables
le_driver = LabelEncoder()
le_team = LabelEncoder()

wet_races['Driver Encoded'] = le_driver.fit_transform(wet_races['Driver Name'])
wet_races['Team Encoded'] = le_team.fit_transform(wet_races['Driver Team'])

# Define features and target for regression
features = ['Air Temperature', 'Relative Humidity', 'Wind Speed', 'Track Temperature',
            'Race Grid Position', 'Driver Encoded', 'Team Encoded', 'Races Before 2024',
            'Team Avg Points', 'Avg Finishing Pos Wet']
target = 'Position'

# Regression: Predict Position
X = wet_races[features]
y = wet_races[target]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Linear Regression Model
regressor = LinearRegression()
regressor.fit(X_train, y_train)

# Predict
y_pred_reg = regressor.predict(X_test)

# Evaluate Regression
mae = mean_absolute_error(y_test, y_pred_reg)
mse = mean_squared_error(y_test, y_pred_reg)
r2 = r2_score(y_test, y_pred_reg)

print("Regression Model Evaluation:")
print(f"MAE: {mae:.2f}")
print(f"MSE: {mse:.2f}")
print(f"R²: {r2:.2f}")

# Coefficients
coefficients = pd.DataFrame({'Feature': features, 'Coefficient': regressor.coef_})
print("\nLinear Regression Coefficients:")
print(coefficients)

# Visualization: Predicted vs Actual Position
plt.figure(figsize=(10, 6))
plt.scatter(y_test, y_pred_reg, color='blue', alpha=0.6, label='Predicted vs Actual')
plt.plot([y.min(), y.max()], [y.min(), y.max()], color='red', linestyle='--', lw=2, label='Ideal Fit')
plt.xlabel('Actual Position')
plt.ylabel('Predicted Position')
plt.title('Regression: Predicted vs Actual Position in Wet Races')
plt.legend()
plt.grid(True)
plt.show()

# Classification: Predict Position as Categorical
wet_races['Position Categorical'] = wet_races['Position'].astype(int)

X_cls = wet_races[features]
y_cls = wet_races['Position Categorical']

# Split data
X_train_cls, X_test_cls, y_train_cls, y_test_cls = train_test_split(X_cls, y_cls, test_size=0.2, random_state=42)

# Train Random Forest Classifier
classifier = RandomForestClassifier(n_estimators=100, random_state=42)
classifier.fit(X_train_cls, y_train_cls)

# Predict
y_pred_cls = classifier.predict(X_test_cls)

# Evaluate Classification
print("\nClassification Model Evaluation:")
print(classification_report(y_test_cls, y_pred_cls))
print("Confusion Matrix:")
print(confusion_matrix(y_test_cls, y_pred_cls))

# Comparative Analysis: Wet vs Dry Races
# Average Position in Wet Races
avg_finishing_wet = wet_races.groupby('Driver Name')['Position'].mean().reset_index()
avg_finishing_wet.rename(columns={'Position': 'Avg Position Wet'}, inplace=True)

# Average Position in Dry Races
dry_races = df_2024_drivers[df_2024_drivers['Rainfall'] == False]
avg_finishing_dry = dry_races.groupby('Driver Name')['Position'].mean().reset_index()
avg_finishing_dry.rename(columns={'Position': 'Avg Position Dry'}, inplace=True)

# Merge Averages
avg_finishing = pd.merge(avg_finishing_wet, avg_finishing_dry, on='Driver Name', how='outer')

# Fill NaN values
avg_finishing['Avg Position Wet'] = avg_finishing['Avg Position Wet'].fillna(avg_finishing['Avg Position Dry'])
avg_finishing['Avg Position Dry'] = avg_finishing['Avg Position Dry'].fillna(avg_finishing['Avg Position Wet'])

# Calculate Improvement
avg_finishing['Position Improvement'] = avg_finishing['Avg Position Dry'] - avg_finishing['Avg Position Wet']

# Visualization: Position Improvement
plt.figure(figsize=(14, 8))
sns.barplot(x='Position Improvement', y='Driver Name', data=avg_finishing, palette='viridis')
plt.title('Driver Position Improvement in Wet Races Compared to Dry Races')
plt.xlabel('Position Improvement (Positive is Better)')
plt.ylabel('Driver Name')
plt.show()
