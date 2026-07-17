# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

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
profile (one of two profiles the runner demonstrates):

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

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this
