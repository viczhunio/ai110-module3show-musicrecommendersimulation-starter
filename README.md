# 🎵 Music Recommender Simulation

## Project Summary

My version of AmbiVibe is a command-line music recommender that scores every song in an 18-track catalog against a listener's taste profile. It returns the top 5 recomendations with an explanation for each. It uses a weighted system to match genre(+2.0), mood(+1.0), energy, and 6 other smaller audio features as tiebreakers. The runner demonstrates three different listeners: deep-focus lofi, upbeat pop, and intense rock. This mirrors real world AI recommenders who use content based filtering with user based filtering, recognzining patterns in the data and among users. 

---

## How The System Works

Real world music recommendation systems analyze patterns from millions of users to predict what a listener would enjoy next. My simulation instead implements **Content-Based Filtering**: rather than relying on crowd-sourced data, it scores each individual track against the user's personal taste profile. It prioritizes a matching genre so tracks outside the user's core taste are penalized, then fine-tunes with mood and how closely a song's energy matches the target.

**What each `Song` stores:** `id`, `title`, `artist`, `genre`, `mood`, and seven numeric features — `energy`, `tempo_bpm`, `valence`, `danceability`, `acousticness`, `instrumentalness`, and `popularity`.

**What the `UserProfile` stores:** a `favorite_genre`, a `favorite_mood`, a `target_energy` (0–1), and `likes_acoustic` (true/false). It can also hold optional targets for the other numeric features.

### Algorithm Recipe

Each song earns a score out of a possible **5.0**, then the top 5 are returned:

| Component | Rule | Points |
|---|---|---|
| **Genre match** | song genre == favorite genre | +2.0 |
| **Mood match** | song mood == favorite mood | +1.0 |
| **Energy similarity** | `1 − |target_energy − song_energy|`, weighted ×1.5 | 0 → 1.5 |
| **Other features** | average closeness of tempo, valence, danceability, acousticness, instrumentalness, popularity, weighted ×0.5 | 0 → 0.5 |

`score = 2.0×genre + 1.0×mood + 1.5×energy_similarity + 0.5×(avg of other features)`

Genre is the strongest signal, mood is worth half as much, and energy is pulled out as its own weighted term so it clearly shapes the ranking while the remaining features act as fine tuning. Songs are ranked highest-to-lowest and the top 5 are shown with a plain-language reason for each.

**Potential biases:** Because genre carries the most weight (2.0), this system might over-prioritize genre — a great song that matches the user's mood and energy but sits in a different genre can be buried beneath weaker same-genre tracks.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Running `python -m src.main` produces the following for the deep-focus lofi
profile (one of three profiles the runner demonstrates):

```
Loaded songs: 18

TOP RECOMMENDATIONS 
Profile: lofi / focused  |  target energy 0.40
==============================================

#1                                Score: 4.99
    Song:   Focus Flow
    Artist: LoRoom
    Genre:  lofi
    Mood:   focused

    Why:
      - genre match: lofi (+2.0)
      - mood match: focused (+1.0)
      - energy match (+1.50)
      - tempo_bpm match (+0.08)
      - valence match (+0.08)
      - danceability match (+0.08)
      - acousticness match (+0.08)
      - instrumentalness match (+0.08)
      - popularity match (+0.08)
----------------------------------------------
#2                                Score: 3.95
    Song:   Midnight Coding
    Artist: LoRoom
    Genre:  lofi
    Mood:   chill

    Why:
      - genre match: lofi (+2.0)
      - energy match (+1.47)
      - tempo_bpm match (+0.08)
      - valence match (+0.08)
      - danceability match (+0.08)
      - acousticness match (+0.08)
      - instrumentalness match (+0.08)
      - popularity match (+0.07)
----------------------------------------------
#3                                Score: 3.90
    Song:   Library Rain
    Artist: Paper Lanterns
    Genre:  lofi
    Mood:   chill

    Why:
      - genre match: lofi (+2.0)
      - energy match (+1.42)
      - tempo_bpm match (+0.08)
      - valence match (+0.08)
      - danceability match (+0.08)
      - acousticness match (+0.07)
      - instrumentalness match (+0.08)
      - popularity match (+0.08)
----------------------------------------------
#4                                Score: 1.88
    Song:   Coffee Shop Stories
    Artist: Slow Stereo
    Genre:  jazz
    Mood:   relaxed

    Why:
      - energy match (+1.46)
      - tempo_bpm match (+0.07)
      - valence match (+0.06)
      - danceability match (+0.07)
      - acousticness match (+0.07)
      - instrumentalness match (+0.07)
      - popularity match (+0.08)
----------------------------------------------
#5                                Score: 1.77
    Song:   Grandma's Porch
    Artist: The Willow Kind
    Genre:  folk
    Mood:   nostalgic

    Why:
      - energy match (+1.40)
      - tempo_bpm match (+0.08)
      - valence match (+0.08)
      - acousticness match (+0.07)
      - popularity match (+0.07)
----------------------------------------------
```

---

## Experiments You Tried

### Feature removal: disabling the mood check

To test how sensitive the rankings are to a single feature, I temporarily
commented out the mood bonus in `score_song` and re-ran all three profiles.

**What happened:** every song that had matched the user's mood lost exactly its
`+1.0`, while mood-mismatched songs were unchanged — confirming the math behaved
as expected. The **#1 pick never changed** for any profile (genre `+2.0` and
energy `×1.5` still dominate), but the mid-list ordering shifted:

| Profile | With mood | Mood removed |
|---|---|---|
| Deep-focus lofi | Focus Flow leads by 1.04 | Focus Flow leads by only 0.04 |
| Upbeat pop | Rooftop Lights #4, Concrete Kingdom #5 | swapped |
| Intense rock | Gym Hero #2, Ashfall #4 | Ashfall jumps to #2 |

**Conclusion — different, not more accurate.** Removing mood let
mood-*mismatched* songs float up: an *aggressive* metal track (Ashfall) rose
above genuinely *intense* rock tracks, and an *energetic* hip-hop song rose
above a *happy* pop one. So mood wasn't dead weight — it does real work as a
**tiebreaker across same-genre and cross-genre songs**. This showed the weight
hierarchy is behaving as designed: genre is the anchor, energy the driver, and
mood the fine-tuner.

---

## Limitations and Risks

This recommender has several limitations. It runs on a tiny catalog of just 18 songs, so there is little variety to draw from. It leans heavily on genre, which can trap a listener in one style and hide good songs from other genres. It also ignores things real listeners care about, like lyrics, language, and listening history. Finally, it does not check for bad input, so an out-of-range value can produce a strange (even negative) score — I explore these issues further in the model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)            

                      
Building this made me realize that a recommender is really just a scoring rule turning data into a ranking. Music platforms have a wide variety of data with each song, and thats how they are able to find the right picks and curate different playlists to different genres, etc. The program compares that data to a listener's profile, awards points for how well they match, and sorts the results. There is no real "understanding" of music happening. 

That's also where bias creeps in. Systems can quietly trap users in one style and hide good songs from similar genres. A model can only "see" the features it was given, and it treats whatever it was told to prioritize as most important — so the people who build it quietly shape what everyone else discovers. A system can reinforce what is already popular, and hide groups that are underrepresented in the data.