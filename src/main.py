"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Taste profile: a "deep-focus / chill lofi" listener.
    # Numeric values are raw here; recommend_songs normalizes them to 0-1 using
    # the library's per-feature ranges before scoring.
    user_prefs = {
        "genre": "lofi",
        "mood": "focused",
        "energy": 0.40,
        "tempo_bpm": 76,
        "valence": 0.55,
        "danceability": 0.60,
        "acousticness": 0.75,
        "instrumentalness": 0.90,
        "popularity": 50,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        # You decide the structure of each returned item.
        # A common pattern is: (song, score, explanation)
        song, score, explanation = rec
        print(f"{song['title']} - Score: {score:.2f}")
        print(f"Because: {explanation}")
        print()


if __name__ == "__main__":
    main()
