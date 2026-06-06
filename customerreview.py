import pandas as pd

# 1. Load the reviews dataset from your local path
reviews = pd.read_csv('/home/moswal/m2/M2Project/olist_order_reviews_dataset.csv')

# 2. Group by 'review_score' and count the occurrences
rating_counts = reviews.groupby('review_score').size().reset_index(name='total_count')

# 3. Sort from highest rating (5 stars) to lowest rating (1 star)
rating_counts = rating_counts.sort_values(by='review_score', ascending=False)

# 4. Calculate the percentage share for better context
rating_counts['percentage'] = ((rating_counts['total_count'] / len(reviews)) * 100).round(2)

# Display the final summary table
print("--- Distribution of Customer Ratings ---")
print(rating_counts.to_string(index=False))
