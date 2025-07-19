from flask import Flask, render_template, request
import pickle
import pandas as pd
from scipy.sparse import hstack

app = Flask(__name__)

# Load all models
knn = pickle.load(open("knn_model.pkl", "rb"))
vectorizer = pickle.load(open("tfidf_vectorizer.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))
books = pd.read_pickle("books_with_tags.pkl")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    mood = request.form['mood']
    pace = request.form['pace']
    genres = request.form.getlist('genres')
    rating = float(request.form['rating'])
    year = int(request.form['year'])

    user_tags = f"{mood}, {pace}, " + ", ".join(genres)
    tag_vec = vectorizer.transform([user_tags])
    num_vec = scaler.transform([[rating, year]])
    user_vec = hstack([tag_vec, num_vec])

    distances, indices = knn.kneighbors(user_vec, n_neighbors=5)
    books['url'] = "https://www.goodreads.com/book/show/" + books['goodreads_book_id'].astype(str)


    recommended_books = books.iloc[indices[0]][[
    'title', 'authors', 'image_url', 'original_title', 'average_rating', 'url'
]].fillna('').to_dict(orient='records')


    return render_template('results.html', books=recommended_books)

if __name__ == '__main__':
    app.run(debug=True)
