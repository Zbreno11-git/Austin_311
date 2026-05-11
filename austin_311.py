import pandas as pd
import matplotlib.pyplot as plt, seaborn as sns

path = '/Users/luanabreno/Desktop/BIGDATA - PROJECT/'
df = pd.read_csv(path + 'bq-results.csv')

print(df.head())
print(df.info())
print(df.describe())

df = df.rename(columns={'unique_key': 'complaints', 'complaint_description': 'department'})

# Transform 'created_date' and 'close_date' into date-time
df['created_date'] = pd.to_datetime(df['created_date'])
df['close_date'] = pd.to_datetime(df['close_date'])

# City names are a mess (AUSTINhttps:/, AUSTIN4413 WHI, aUSTIN, etc.)
df['city'] = df['city'].str.upper().str.strip()
df['city'] = df['city'].str.replace(r'AUSTIN.*', 'AUSTIN', regex=True)
df['city'] = df['city'].replace({
    'DRIPPING SPRIN': 'DRIPPING SPRING', 'ELGEN': 'ELGIN', 'WILLIAMSON COU': 'WILLIAMSON COUNTY'
})
df['city'] = df['city'].fillna('AUSTIN')
city_counts = df['city'].value_counts()
lower_counts = city_counts[city_counts < 50].index
    # Grouping cities with lower incidents counts
df.loc[df['city'].isin(lower_counts), 'city'] = 'OTHER'

    # Gonna group the complaints into categories since we have 255 different descriptions
def categorize(desc):
    desc = str(desc).upper()

    # ANIMAL
    if any(x in desc for x in
           ['ANIMAL', 'DOG', 'CAT', 'COYOTE', 'PET', 'WILDLIFE', 'BITE', 'TRAPPED', 'VICIOUS', 'LOOSE', 'STRAY',
            'ROADKILL', 'DEAD ANIMAL']):
        return 'ANIMAL'
    # CODE COMPLIANCE
    elif any(x in desc for x in
             ['ACD', 'DSD', 'CODE', 'BILLBOARD', 'CONSTRUCTION', 'RENTAL', 'ZONING', 'ALARM', 'HAULER',
              'OUTDOOR COMMERCIAL', 'TREE AND ENVIRONMENTAL']):
        return 'CODE COMPLIANCE'
    # STREET/TRAFFIC
    elif any(x in desc for x in
             ['TPW', 'ATD', 'SBO', 'PW', 'PWD', 'POTHOLE', 'STREET', 'TRAFFIC', 'SIGNAL', 'SIGN', 'PAVEMENT', 'ROAD',
              'CURB', 'GUTTER', 'BRIDGE', 'ALLEY', 'MARKINGS', 'STRIPING', 'PEDESTRIAN', 'BICYCLE', 'SIDEWALK',
              'MOWING', 'OBSTRUCTION', 'SPILLAGE', 'GUARDRAIL', 'SPEED MANAGEMENT']):
        return 'STREET/TRAFFIC'
    # WATER/DRAINAGE
    elif any(x in desc for x in
             ['AW', 'WPD', 'WATER', 'LEAK', 'DRAIN', 'FLOOD', 'SEWER', 'WATERSHED', 'EROSION', 'STANDING WATER',
              'DITCH', 'POND', 'CHANNEL', 'CREEK', 'STORM DRAIN', 'ALGAE', 'EMERGENCY WATER']):
        return 'WATER/DRAINAGE'
    # TRASH/DEBRIS
    elif any(x in desc for x in
             ['ARR', 'TRASH', 'GARBAGE', 'DEBRIS', 'DUMPING', 'BULK', 'RECYCLING', 'COMPOST', 'BRUSH', 'SPILLAGE',
              'HAZARDOUS WASTE', 'STORM DEBRIS', 'COLLECTION']):
        return 'TRASH/DEBRIS'
    # PARKS/RECREATION
    elif any(x in desc for x in
             ['PARK', 'PARD', 'PLAYGROUND', 'TRAIL', 'TREE', 'CEMETERIES', 'AQUATIC', 'GROUNDS', 'BUILDING ISSUES']):
        return 'PARKS/RECREATION'
    # NOISE/POLICE
    elif any(x in desc for x in
             ['APD', 'NOISE', 'LOUD', 'MUSIC', 'ALARM', 'NON EMERGENCY', 'VEHICLE ABATEMENT', 'HANDS FREE',
              'COLLISION']):
        return 'NOISE/POLICE'
    # GRAFFITI
    elif 'GRAFFITI' in desc:
        return 'GRAFFITI'
    # LIGHTING/ENERGY
    elif any(x in desc for x in
             ['AE', 'LIGHT', 'OUTAGE', 'POWER', 'ENERGY', 'STREETLIGHT', 'ELECTRIC VEHICLE', 'KEY ACCOUNTS']):
        return 'LIGHTING/ENERGY'
    # FIRE/SAFETY
    elif any(x in desc for x in ['AFD', 'FIREWORKS', 'WILDFIRE']):
        return 'FIRE/SAFETY'
    # HEALTH
    elif any(x in desc for x in ['APH', 'HEALTH', 'CORONAVIRUS', 'COVID', 'EQUITY LINE', 'ENVIRONMENTAL HEALTH']):
        return 'HEALTH'
    # PARKING/TRANSPORT
    elif any(x in desc for x in ['PARKING', 'BOOTING', 'PAY-BY-PHONE', 'PARKING MACHINE', 'SHARED MICROMOBILITY']):
        return 'PARKING/TRANSPORT'
    # UTILITY/TELECOM
    elif any(x in desc for x in ['TELECOMMUNICATION', 'GAS UTILITY', 'TARA', 'UTILITY CUT']):
        return 'UTILITY/TELECOM'
    # HOUSING/COMMUNITY
    elif any(x in desc for x in
             ['HD', 'HPD', 'NEIGHBORHOOD HOME', 'COMMUNITY VOICES', 'COMMUNITY ENGAGEMENT', 'COMMUNITY CONNECTIONS']):
        return 'HOUSING/COMMUNITY'
    # GENERAL/311
    elif any(x in desc for x in
             ['311', 'CRIS', 'CC', 'CPIO', 'CORRIDOR', 'HSEM', 'SBO', 'CLIENT', 'COMMAND CENTER', 'OTHER']):
        return 'GENERAL/311'
    else:
        return 'OTHER'

df['complaints'] = df['complaints'].apply(categorize)

print(df[df['complaints'] == 'OTHER']['complaints'].value_counts().head(20))

print(df['complaints'].value_counts())
print(df['complaints'].unique())

    # Cutting outliers (1%)
upper = df['days_to_resolve'].quantile(0.99)
df_clean = df[df['days_to_resolve'] <= upper]

# Average days to resolve the issue of each category
complaint_resolve = df_clean.groupby('complaints')['days_to_resolve'].agg(['mean', 'median', 'count']).sort_values('mean')
#print(complaint_resolve)
"""
                        mean  median   count
complaints                                  
OTHER               0.000000     0.0       1
GENERAL/311         0.260132     0.0   28993
FIRE/SAFETY         2.274023     1.0    3788
STREET/TRAFFIC      5.270408     1.0  235633
CODE COMPLIANCE     5.339613     0.0  183462
ANIMAL              5.593101     1.0  150541
LIGHTING/ENERGY     6.965352     4.0     837
WATER/DRAINAGE      6.997151     1.0   25976
HOUSING/COMMUNITY   9.447955     5.0     538
HEALTH              9.813209     1.0    3437
GRAFFITI           15.117482     5.0    3924
PARKS/RECREATION   17.543841     5.0   26037
TRASH/DEBRIS       17.712829     3.0  260138
NOISE/POLICE       18.722315    13.0   50514
"""
# Complaints Viz
sns.set_style('darkgrid')
sns.barplot(y = complaint_resolve.index.drop('OTHER'),
            x = complaint_resolve['mean'].drop('OTHER'),
            hue = complaint_resolve.index.drop('OTHER'),
            palette = 'Reds', orient = 'h')
plt.ylabel('Complaints')
plt.xlabel('Days to Resolve - Mean')
plt.xticks(rotation=45)
plt.tight_layout()
#plt.show()

    # Preparing for ML
df['month'] = df['created_date'].dt.month
df['weekday'] = df['created_date'].dt.weekday
df['hour'] = df['created_date'].dt.hour

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

    # Classification

# I tried using 3 categories, but the model fails a lot with the Medium category.
def classification(days):
    if days <= 7:
        return 'Fast'
    else:
        return 'Slow'

df['resolution_class'] = df['days_to_resolve'].apply(classification)

X = df.drop(['status', 'close_date', 'department', 'days_to_resolve', 'created_date', 'resolution_class'], axis=1)
X = pd.get_dummies(X, columns=['city', 'complaints'], drop_first=True)

y = df['resolution_class']

le = LabelEncoder()
y = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

XG = XGBClassifier(n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=3.55,
    random_state=42,
    n_jobs=-1
)
XG.fit(X_train, y_train)
probs = XG.predict_proba(X_test)[:, 1]
pred = (probs > 0.45).astype(int)

print(f'Classification Report: {classification_report(y_test, pred)}')
print(f'Confusion Matrix: {confusion_matrix(y_test, pred)}')
print(f'ROC AUC: {roc_auc_score(y_test, probs)}')

"""
ROC AUC: 0.785... - The model ranks a critical SLOW case above a FAST case 78.5% of the time.

Trade off - Threshold 0.45:
- Recall SLOW: 67% - Catches 2 out of 3 cases that will actually be delayed.
- Precision SLOW: 43% - 4 out of 10 alerts are real delays

For 311 operations, FP are cheaper than FN.
"""

cm = confusion_matrix(y_test, pred, labels=[0, 1])

df_cm = pd.DataFrame(cm, index=["Actual Fast", "Actual Slow"],
                     columns=["Pred Fast", "Pred Slow"])

df_cm = df_cm.reset_index().rename(columns={'index':'Actual'})
df_cm = df_cm.melt(id_vars=['Actual'], var_name='Predicted', value_name='Count')

print(df_cm)
print(df_clean.head())

df_cm.to_csv('cm_df_311.csv', index=False)
df_clean.to_csv('df_clean_311.csv', index=False)