import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# Numeric features compared during scoring. Genre and mood are categorical and
# handled separately (see score_song). tempo_bpm and popularity are NOT on a
# 0-1 scale in the raw data, so every numeric feature is min-max normalized to
# 0-1 before distances are computed (see compute_feature_ranges / normalize_value).
NUMERIC_FEATURES = [
    "energy",
    "tempo_bpm",
    "valence",
    "danceability",
    "acousticness",
    "instrumentalness",
    "popularity",
]

# Weighted-hybrid scoring weights.
#
# Genre and mood are categorical (yes/no) bonuses. Energy is pulled OUT of the
# averaged numeric bucket and given its own, heavier weight so it clearly drives
# the ranking; the remaining numeric features are averaged together and kept as a
# quieter fine-tuning term. Max possible score = 2.0 + 1.0 + 1.5 + 0.5 = 5.0.
GENRE_BONUS = 2.0
MOOD_BONUS = 1.0
ENERGY_WEIGHT = 1.5   # energy_similarity (raw 0-1) is multiplied by this
OTHER_WEIGHT = 0.5    # avg similarity of the remaining numeric features

# A feature is "close" enough to be worth mentioning in the reasons list when
# its similarity clears this bar. Lower = more (weaker) reasons shown per song.
CLOSE_MATCH_THRESHOLD = 0.75


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py

    instrumentalness and popularity have defaults so existing callers/tests that
    construct a Song without them keep working.
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    instrumentalness: float = 0.0
    popularity: float = 0.0


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    The first four fields are the starter contract. The optional target_* fields
    let a profile express preferences over the richer feature set; when left as
    None they are simply not used in scoring.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_tempo_bpm: Optional[float] = None
    target_valence: Optional[float] = None
    target_danceability: Optional[float] = None
    target_acousticness: Optional[float] = None
    target_instrumentalness: Optional[float] = None
    target_popularity: Optional[float] = None


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def compute_feature_ranges(songs: List[Dict]) -> Dict[str, Tuple[float, float]]:
    """
    Compute the (min, max) of each numeric feature across the whole library.

    This is a library-wide pass on purpose: min-max scaling needs the range of
    the full corpus, so it cannot be done one song at a time inside score_song.
    """
    ranges: Dict[str, Tuple[float, float]] = {}
    for feature in NUMERIC_FEATURES:
        values = [
            float(song[feature])
            for song in songs
            if feature in song and song[feature] is not None
        ]
        if values:
            ranges[feature] = (min(values), max(values))
    return ranges


def normalize_value(value: float, lo: float, hi: float) -> float:
    """
    Min-max scale a single value to 0-1, clamped to [0, 1].

    Returns 0.0 when the feature has no spread (hi == lo) so a constant feature
    contributes nothing rather than dividing by zero.
    """
    if hi <= lo:
        return 0.0
    scaled = (value - lo) / (hi - lo)
    return max(0.0, min(1.0, scaled))


def _add_scaled(obj: Dict, ranges: Dict[str, Tuple[float, float]]) -> Dict:
    """
    Return a copy of a song dict (or a prefs dict) with a `<feature>_scaled`
    companion for every numeric feature present. Raw values are kept so
    explanations can still report real bpm / popularity, etc.
    """
    out = dict(obj)
    for feature, (lo, hi) in ranges.items():
        if feature in out and out[feature] is not None:
            out[feature + "_scaled"] = normalize_value(float(out[feature]), lo, hi)
    return out


# ---------------------------------------------------------------------------
# Scoring (functional path used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file into a list of dicts with typed fields.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "instrumentalness": float(row["instrumentalness"]),
                "popularity": float(row["popularity"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.

    Both `user_prefs` and `song` carry `<feature>_scaled` values (added by
    recommend_songs via _add_scaled) alongside their raw values. The "other"
    numeric features are compared on their normalized (_scaled) values; energy
    is compared on its RAW 0-1 value and weighted on its own (see module weights).

    Returns (score, reasons).
    """
    reasons: List[str] = []
    score = 0.0

    # Categorical bonuses (the headline weights). Shown first so the biggest
    # contributors lead the explanation.
    if user_prefs.get("genre") and song.get("genre") == user_prefs.get("genre"):
        score += GENRE_BONUS
        reasons.append(f"genre match: {song.get('genre')} (+{GENRE_BONUS:.1f})")
    if user_prefs.get("mood") and song.get("mood") == user_prefs.get("mood"):
        score += MOOD_BONUS
        reasons.append(f"mood match: {song.get('mood')} (+{MOOD_BONUS:.1f})")

    # Energy similarity: its own, heavier-weighted term. Energy is already on a
    # 0-1 scale, so it is compared raw (no normalization needed).
    energy_similarity = 0.0
    if "energy" in user_prefs and "energy" in song:
        energy_similarity = 1.0 - abs(user_prefs["energy"] - song["energy"])
    energy_points = ENERGY_WEIGHT * energy_similarity
    score += energy_points
    if energy_similarity >= CLOSE_MATCH_THRESHOLD:
        reasons.append(f"energy match (+{energy_points:.2f})")

    # Other numeric features: compared on their normalized (_scaled) values and
    # averaged together, then weighted. Because they share OTHER_WEIGHT via an
    # average, each feature's marginal contribution is
    # OTHER_WEIGHT * similarity / (number of other features scored).
    other_pairs: List[Tuple[str, float]] = []
    for feature in NUMERIC_FEATURES:
        if feature == "energy":
            continue
        key = feature + "_scaled"
        if key in user_prefs and key in song:
            other_pairs.append((feature, 1.0 - abs(user_prefs[key] - song[key])))

    if other_pairs:
        other_avg = sum(sim for _, sim in other_pairs) / len(other_pairs)
        score += OTHER_WEIGHT * other_avg
        # Only mention features that clear the closeness bar, each with the
        # points it actually added.
        for feature, similarity in other_pairs:
            if similarity >= CLOSE_MATCH_THRESHOLD:
                points = OTHER_WEIGHT * similarity / len(other_pairs)
                reasons.append(f"{feature} match (+{points:.2f})")

    if not reasons:
        reasons.append("general similarity to your taste")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Normalizes the whole library once, scales the profile's targets with the
    SAME ranges, scores every song, and returns the top-k as
    (raw_song_dict, score, explanation).
    """
    if not songs:
        return []

    ranges = compute_feature_ranges(songs)
    prepared_prefs = _add_scaled(user_prefs, ranges)

    scored: List[Tuple[Dict, float, str]] = []
    for song in songs:
        prepared_song = _add_scaled(song, ranges)
        score, reasons = score_song(prepared_prefs, prepared_song)
        # Return the raw song dict (not the scaled copy) so callers see real values.
        scored.append((song, score, "; ".join(reasons)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


# ---------------------------------------------------------------------------
# OOP path used by tests/test_recommender.py
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py

    Thin adapter over the functional scoring pipeline: converts Song objects and
    UserProfile into plain dicts, delegates to recommend_songs / score_song, then
    maps results back to Song objects.
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    @staticmethod
    def _song_dict(song: Song) -> Dict:
        return {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "mood": song.mood,
            "energy": song.energy,
            "tempo_bpm": song.tempo_bpm,
            "valence": song.valence,
            "danceability": song.danceability,
            "acousticness": song.acousticness,
            "instrumentalness": getattr(song, "instrumentalness", 0.0),
            "popularity": getattr(song, "popularity", 0.0),
        }

    @staticmethod
    def _user_prefs(user: UserProfile) -> Dict:
        prefs: Dict = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
        }
        optional_targets = [
            ("target_tempo_bpm", "tempo_bpm"),
            ("target_valence", "valence"),
            ("target_danceability", "danceability"),
            ("target_acousticness", "acousticness"),
            ("target_instrumentalness", "instrumentalness"),
            ("target_popularity", "popularity"),
        ]
        for attr, key in optional_targets:
            value = getattr(user, attr, None)
            if value is not None:
                prefs[key] = value

        # Translate the boolean likes_acoustic into an acousticness target when
        # the profile didn't set one explicitly.
        if "acousticness" not in prefs:
            prefs["acousticness"] = 1.0 if user.likes_acoustic else 0.0

        return prefs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        song_dicts = [self._song_dict(s) for s in self.songs]
        prefs = self._user_prefs(user)
        ranked = recommend_songs(prefs, song_dicts, k)

        id_to_song = {s.id: s for s in self.songs}
        return [id_to_song[item[0]["id"]] for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        song_dicts = [self._song_dict(s) for s in self.songs]
        ranges = compute_feature_ranges(song_dicts)

        prepared_prefs = _add_scaled(self._user_prefs(user), ranges)
        prepared_song = _add_scaled(self._song_dict(song), ranges)
        score, reasons = score_song(prepared_prefs, prepared_song)

        return f"'{song.title}' scored {score:.2f}: " + "; ".join(reasons)