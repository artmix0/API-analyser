import requests
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

BASE_URL = "https://jsonplaceholder.typicode.com"

st.set_page_config(page_title="API Analytics", layout="wide")

st.title("Analityka Danych z JSONPlaceholder API")

@st.cache_data
def fetch_data(endpoint):
    response = requests.get(f"{BASE_URL}/{endpoint}")
    response.raise_for_status()
    return response.json()

# Pobieranie danych z 3 endpointów
users = pd.DataFrame(fetch_data("users"))
posts = pd.DataFrame(fetch_data("posts"))
comments = pd.DataFrame(fetch_data("comments"))
todos = pd.DataFrame(fetch_data("todos"))

st.subheader("Wyliczone metryki")

# Liczba postów na użytkownika
posts_per_user = posts.groupby("userId").size().reset_index(name="posts_count")
posts_per_user = posts_per_user.merge(users[["id", "name"]], left_on="userId", right_on="id")

# Średnia liczba komentarzy na post
comments_per_post = comments.groupby("postId").size().reset_index(name="comments_count")
avg_comments = comments_per_post["comments_count"].mean()

# Procent wykonanych todo przez użytkowników
todo_stats = todos.groupby("userId")["completed"].mean().reset_index()
todo_stats["completed_percent"] = todo_stats["completed"] * 100
todo_stats = todo_stats.merge(users[["id", "name"]], left_on="userId", right_on="id")

# Top 5 najbardziej komentowanych postów
top_posts = comments_per_post.sort_values("comments_count", ascending=False).head(5)
top_posts = top_posts.merge(posts[["id", "title"]], left_on="postId", right_on="id")

col1, col2, col3 = st.columns(3)

col1.metric("Średnia liczba komentarzy na post", f"{avg_comments:.2f}")
col2.metric("Liczba użytkowników", len(users))
col3.metric("Liczba wszystkich postów", len(posts))

st.markdown("---")

# WYKRES – liczba postów na użytkownika

st.subheader("Liczba postów na użytkownika")

fig1, ax1 = plt.subplots()
ax1.bar(posts_per_user["name"], posts_per_user["posts_count"])
ax1.set_xticklabels(posts_per_user["name"], rotation=45, ha="right")
ax1.set_ylabel("Liczba postów")
ax1.set_xlabel("Użytkownik")

st.pyplot(fig1)

# WYKRES 2 – procent wykonanych todo przez użytkowników

st.subheader("Procent wykonanych TODO przez użytkowników")

fig2, ax2 = plt.subplots()
ax2.pie(todo_stats["completed_percent"],
        labels=todo_stats["name"],
        autopct="%1.1f%%")
st.pyplot(fig2)

# Tabela Top 5

st.subheader("Top 5 najbardziej komentowanych postów")

st.dataframe(top_posts[["title", "comments_count"]])
