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
    print(f"Loaded songs: {len(songs)}")

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

    divider = "-" * 46
    print("\nTOP RECOMMENDATIONS")
    print(f"Profile: {user_prefs['genre']} / {user_prefs['mood']}"
          f"  |  target energy {user_prefs['energy']:.2f}")
    print("=" * 46)
    print()
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        # Rank on the left, score right-aligned.
        print(f"{'#' + str(rank):<34}Score: {score:.2f}")
        print(f"    {'Song:':<8}{song['title']}")
        print(f"    {'Artist:':<8}{song['artist']}")
        print(f"    {'Genre:':<8}{song['genre']}")
        print(f"    {'Mood:':<8}{song['mood']}")
        print()
        print("    Why:")
        # recommend_songs joins the reasons with '; '; split them back out so
        # each reason (with its point contribution) sits on its own line.
        for reason in explanation.split("; "):
            print(f"      - {reason}")
        print(divider)


if __name__ == "__main__":
    main()
