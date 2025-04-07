from database.mongo_services import get_data_schedules
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

df = get_data_schedules()
df = pd.DataFrame(df)
df['description'] = df['description'].fillna('')

user_ids = df['userId'].unique()

for user_id in user_ids:
    print(f"\n==== Gợi ý cho người dùng: {user_id} ====")
    user_history = df[df['userId'] == user_id]

    if user_history.empty:
        print("→ Không có lịch trình nào để gợi ý.")
        continue

    user_profile_text = " ".join(user_history['description'].astype(str))
    all_descriptions = df['description'].tolist()
    all_descriptions.append(user_profile_text)

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_descriptions)

    user_vector = tfidf_matrix[-1]
    cosine_sim = cosine_similarity(user_vector, tfidf_matrix[:-1]).flatten()

    df['similarity'] = cosine_sim
    top_n = 3
    recommendations = df.sort_values(by='similarity', ascending=False).head(top_n)

    for _, row in recommendations.iterrows():
        print(f"- {row['name']} | {row['description']} | Similarity: {row['similarity']:.2f}")
