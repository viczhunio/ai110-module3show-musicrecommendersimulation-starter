# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**AmbiVibe**  

---

## 2. Intended Use  

The app is intended to generate a list of similar tracks based on a user's profile. It assumes the style of music the user wants to hear. The app is for classroom exploration, using a mock dataset. 

---

## 3. How the Model Works  

The app gives every song a score for one listener. Then it returns the songs with the highest scores. To determine the score, it looks at the song's genre, mood, and energy. It also checks smaller details like tempo, danceability, and popularity. The listener gives a taste profile with their favorite genre, mood, and energy. The score is a points system, with genre match as the most points. The starter version only used genre, mood, and energy in a simple way. I added more song details, and gave genre and mood clear point values. I made energy its own strong factor. I also made the app explain the points behind each pick. 

---

## 4. Data  

The catalog is a small mock dataset. It has 18 songs, and 14 genres. These include pop, lofi, rock, jazz, hip-hop, soul/r&b, metal, and more. They also cover 11 moods, like happy, chill, intense, sad, and focused. Each song has a genre, a mood, and several number traits. Those traits are energy, tempo, valence, danceability, acousticness, instrumentalness, and popularity. I added two columns to the starter data: instrumentalness and popularity. This gave the model more detail to score on. The dataset is small so it leaves a lot of music out. Most genres have only one song. There is no classical, country, or much world music. The data also has no lyrics and no listening history.           

---

## 5. Strengths  

The system works best for listeners with a clear, consistent taste. When someone's genre, mood, and energy all point the same way, the top pick is spot on. It also gives different results to different people. The three test listeners each got a different #1 song. The app does not just hand everyone the same popular track. The app also explains its decisions, every pick shows the points behind it. This makes the recommendations easy to trust and check.

---

## 6. Limitations and Bias 

The biggest weakness I discovered during testing is a genre filter bubble created by the heavy `+2.0` genre weight. A genre match is worth more than a perfect energy match (1.5) and far more than any single other feature(~0.08). Because of that, same-genre songs almost always fill the top of the list. With the Lofi profile the top three results were all lofi, and the mood-removal experiment confirmed that genre and energy alone decide the #1 pick. This means a listener is rarely shown a great song from an adjacent genre, so the system reinforces existing taste instead of encouraging discovery. The problem is compounded by exact-string genre matching: `"indie pop"` does not match `"pop"`. Closely related subgenres are penalized as if they were completely different. With 14 genres spread across only 18 songs, most genres have a single track, so once the genre filter narrows the field there is almost no variety left to rank.

---

## 7. Evaluation  

### Comparing the three profiles (pairwise)

I ran three everyday listeners — **deep-focus lofi**, **upbeat pop**, and
**intense rock** — and compared how their top-5 lists differ. Comparing them in
pairs shows the preferences are actually testing for different things.

- **Lofi vs. Pop:** These two lists share *no* songs. The lofi listener gets
  quiet, mellow background music, while the pop listener gets bright, upbeat tracks. This makes sense because they ask for opposite energy levels (0.40 vs.
  0.80) and different genres.

- **Lofi vs. Rock:** The most opposite pair with no overlap. Lofi is
  calm and slow; rock is loud, fast, and aggressive. The huge energy gap (0.40 vs. 0.90) pushes each listener to the opposite end of the catalog, which is exactly what we'd expect.

- **Pop vs. Rock:** Unlike the other pairs, these two overlap and both lists include Gym Hero and Sunrise City. That happens because both listeners want high energy. Energetic songs bubble up for each of them even if the genres differ.  

**Why does "Gym Hero" keep showing up for a "Happy Pop" fan?** 
Gym Hero is a pop song that is *very* high-energy, but it's tagged with the mood
"intense" rather than "happy." When someone asks for happy pop, the system gives
Gym Hero a big bonus just for being *pop*, and another big reward for being
*high-energy* (which happy pop usually is). Those two rewards are so large that
the mismatched "intense" mood isn't enough to keep it out of the top list. So a
happy-pop fan keeps seeing an intense workout track — a good, concrete example
of the genre-and-energy weighting overpowering mood.

### Adversarial / edge-case profiles

Beyond the three "normal" profiles (deep-focus lofi, upbeat pop, intense rock),
I stress-tested the scoring logic with **adversarial / edge-case profiles**
designed to try to trick it. Each was run through the recommender and the top 5
results observed in the terminal.

### Adversarial Profile 1 — Conflicting Signals (sad + high energy)

A `soul/r&b`, `sad` listener who also asks for `energy = 0.9`. Sad songs are
almost always low-energy, so this pits the categorical bonuses against a
mismatched energy target.

```
TOP RECOMMENDATIONS - CONFLICTING SIGNALS (sad + high energy)
Profile: soul/r&b / sad  |  target energy 0.90
==============================================

#1                                Score: 3.60
    Song:   Empty Side of Bed
    Artist: Noor Amara
    Genre:  soul/r&b
    Mood:   sad

    Why:
      - genre match: soul/r&b (+2.0)
      - mood match: sad (+1.0)
----------------------------------------------
#2                                Score: 2.87
    Song:   Velvet Hours
    Artist: Mara Sol
    Genre:  soul/r&b
    Mood:   romantic

    Why:
      - genre match: soul/r&b (+2.0)
----------------------------------------------
#3                                Score: 1.48
    Song:   Storm Runner
    Artist: Voltline
    Genre:  rock
    Mood:   intense

    Why:
      - energy match (+1.48)
----------------------------------------------
```

**Observation:** "Empty Side of Bed" wins even though its energy (0.30) is the
opposite of the requested 0.90 — the genre + mood bonus (+3.0) overwhelms the
energy mismatch, and the energy reason doesn't even appear (it fell below the
0.75 closeness bar). The system trusts the *labels* over the conflicting
*number*. Arguably correct (a sad-soul fan probably does want this song), but it
shows energy can be completely ignored when the categorical match is strong.

### Adversarial Profile 2 — Ghost Genre (a genre not in the catalog)

Genre `polka`, which no song has, plus `happy` / `energy 0.5`.

```
TOP RECOMMENDATIONS - GHOST GENRE (polka not in catalog)
Profile: polka / happy  |  target energy 0.50
==============================================

#1                                Score: 2.11
    Song:   Rooftop Lights
    Artist: Indigo Parade
    Genre:  indie pop
    Mood:   happy

    Why:
      - mood match: happy (+1.0)
----------------------------------------------
#2                                Score: 2.05
    Song:   Payday Strut
    Artist: Brass Cartel
    Genre:  funk
    Mood:   happy

    Why:
      - mood match: happy (+1.0)
----------------------------------------------
#3                                Score: 2.02
    Song:   Sunrise City
    Artist: Neon Echo
    Genre:  pop
    Mood:   happy

    Why:
      - mood match: happy (+1.0)
----------------------------------------------
```

**Observation:** The system degrades gracefully. With the +2.0 genre bonus
unreachable, it simply falls back to ranking on mood and energy, surfacing happy
songs. No crash, no empty result — a good sign for robustness.

### Adversarial Profile 3 — Out-of-Range Energy (energy = 2.0)

An invalid `energy = 2.0` (the valid range is 0–1), with `pop` / `happy`.

```
TOP RECOMMENDATIONS - OUT-OF-RANGE ENERGY (energy = 2.0)
Profile: pop / happy  |  target energy 2.00
==============================================

#1                                Score: 2.73
    Song:   Sunrise City
    Artist: Neon Echo
    Genre:  pop
    Mood:   happy

    Why:
      - genre match: pop (+2.0)
      - mood match: happy (+1.0)
----------------------------------------------
#4                                Score: 0.64
    Song:   Rooftop Lights
    Artist: Indigo Parade
    Genre:  indie pop
    Mood:   happy

    Why:
      - mood match: happy (+1.0)
----------------------------------------------
#5                                Score: -0.05
    Song:   Ashfall
    Artist: Iron Verdict
    Genre:  metal
    Mood:   aggressive

    Why:
      - general similarity to your taste
----------------------------------------------
```

**Observation — the most surprising result:** the last song scored a **negative
number** (-0.05). Because energy is compared raw and *not clamped*, an
out-of-range target makes `1 − |2.0 − song_energy|` go negative, which the ×1.5
weight then multiplies into a negative contribution. The scoring never validates
that inputs are in range. This is a real edge-case bug: the system should either
clamp energy to [0, 1] or reject invalid profiles.

### What I looked for and what surprised me             
                     
- I was looking to see if strong categorical matches could hide a huge numeric mismatch, this is seen in Profile 1. I also wanted to see if an unmatchable genre would break it, which in Profile 2 is seen to just degrade smoothly. I also looked to see if bad input is handled, Profile 3 shows that a negative score is produced. The most suprising for me was the negative score is possible with out of range input. 

### Sensitivity Test — removing the mood feature

As a second evaluation, I measured how much one feature matters by temporarily
disabling the mood bonus and comparing rankings.

- **Result:** the top recommendation for each profile stayed the same, because
  genre and energy carry most of the weight. However, lower-ranked positions
  reshuffled — songs that no longer earned mood points were overtaken by
  mood-mismatched songs (e.g., for the intense-rock listener, the *aggressive*
  track "Ashfall" rose from #4 to #2 above genuinely *intense* tracks). What this shows is that mood has little effect on the single best pick but a
  real effect on the ordering of the rest of the list. It acts as a tiebreaker
  rather than a primary signal. The system leans heavily on genre and can
  under-weight mood and energy when ranking the top result.

---

## 8. Future Work  

I would like to fix the out of range energy, so a good fix would be to reject bad profiles or validate ranges. I would also like to improve genre matching, making it so that "Indie pop" would slightly match with "pop." Related genres could have more of a match. I would also be interested in adding an aspect where the user can pick more than one favorite genre or mood. They could choose what matters most to them.           
                
---

## 9. Personal Reflection  

I learned that recommender systems are really all about scoring. They go through patterns and match what a user would like. The most surprising thing for me was how much one weight can take over. My genre bonus was very strong and created a filter bubble. Songs from other genres rarely broke through. This changed how I think about music apps because when an apps keeps showing me the same kind of song, that is intentional. These apps learn from your tastes and favorites, to bring reccomendations you would like. 