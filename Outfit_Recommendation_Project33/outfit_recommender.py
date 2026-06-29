



import random
from py.recognition_module import single_classification, color_classification, find_combo_by_top, COLOR_GROUP_INDEX

OCCASION_SIMILARITY = {
    "Casual":       {"Casual": 0, "Smart Casual": 1, "Sports": 1, "Party": 2, "Ethnic": 3, "Formal": 3},
    "Smart Casual": {"Smart Casual": 0, "Casual": 1, "Formal": 1, "Party": 1, "Ethnic": 2, "Sports": 2},
    "Formal":       {"Formal": 0, "Smart Casual": 1, "Party": 1, "Ethnic": 1, "Casual": 3, "Sports": 3},
    "Party":        {"Party": 0, "Smart Casual": 1, "Formal": 1, "Casual": 2, "Ethnic": 2, "Sports": 3},
    "Sports":       {"Sports": 0, "Casual": 1, "Smart Casual": 2, "Ethnic": 3, "Formal": 3, "Party": 3},
    "Ethnic":       {"Ethnic": 0, "Formal": 1, "Party": 2, "Smart Casual": 2, "Casual": 3, "Sports": 3},
}

VALID_USAGE = ['Casual', 'Ethnic', 'Formal', 'Party', 'Smart Casual', 'Sports']


class OutfitRecommender:
    def __init__(self):
        self.top = []
        self.bottom = []
        self.shoes = []


    # -------------------------------
    # Add a clothing item
    # -------------------------------
    def add_image(self, image_path):
        """
        Classify the image and store it as a flat dictionary.
        Returns subtype and full info.
        """
        subtype, info_str, res_dict = single_classification(image_path)

        # Store in the correct category
        if subtype == "top":
            self.top.append(res_dict)
        elif subtype == "bottom":
            self.bottom.append(res_dict)
        elif subtype == "foot":
            self.shoes.append(res_dict)
        else:
            # fallback: store in top if unknown subtype
            self.top.append(res_dict)

        return subtype, res_dict

    # -------------------------------
    # Occasion similarity helper
    # -------------------------------
    def occasions_within(self, usage, max_distance):
        """Return all occasions within max_distance of the requested one (inclusive)."""
        table = OCCASION_SIMILARITY[usage]
        return {o for o, d in table.items() if d <= max_distance}

    # -------------------------------
    # Occasion filtering (optional) — pulled out of generate_outfit
    # -------------------------------
    def _filter_by_occasion(self, usage):
        """
        Given a requested occasion (or None), return the candidate top/bottom/shoe
        pools to use, plus how far the search had to widen to find a full outfit.

        - usage is None  -> no occasion filtering at all; returns the entire wardrobe.
        - usage is a string -> normalized (case-insensitive) against VALID_USAGE.
          If it doesn't match any valid occasion, returns (None, None, None, None)
          to signal "invalid occasion."
          Otherwise tries an exact match first (distance 0), then widens to
          progressively "less similar" occasions (distance 1, 2, 3) until a tier
          is found where top, bottom, AND shoes pools are all non-empty.

        Returns: (tops, bottoms, shoes, matched_distance)
            matched_distance is None when usage was None (no filtering applied),
            0 when an exact match was found, or 1/2/3 if widening was needed.
            tops is None (with bottoms/shoes also None) if usage was invalid,
            or if even the widest search found an empty category.
        """
        if usage is not None:
            usage_lookup = {u.lower(): u for u in VALID_USAGE}
            normalized = usage_lookup.get(usage.strip().lower())
            if normalized is None:
                return None, None, None, None  # unrecognized occasion string
            usage = normalized

        def build_candidates(allowed_usages):
            if allowed_usages is None:
                return self.top, self.bottom, self.shoes
            tops = [t for t in self.top if t.get("usage") in allowed_usages]
            bottoms = [b for b in self.bottom if b.get("usage") in allowed_usages]
            shoes = [s for s in self.shoes if s.get("usage") in allowed_usages]
            return tops, bottoms, shoes

        if usage is None:
            search_steps = [(None, None)]  # no occasion filtering at all
        else:
            search_steps = [
                (self.occasions_within(usage, dist), dist)
                for dist in range(0, 4)  # 0 = exact, up to 3 = everything
            ]

        for allowed_usages, dist in search_steps:
            tops, bottoms, shoes = build_candidates(allowed_usages)
            if tops and bottoms and shoes:
                return tops, bottoms, shoes, dist

        # Even with every occasion allowed, some category is completely empty
        return None, None, None, None

    # -------------------------------
    # Generate Outfit
    # -------------------------------
    def generate_outfit(self, toseason=None, gender=None, usage=None, combotype=60):
        """
        Generate an outfit with optional gender/season/occasion(usage) filtering.

        Occasion (usage) is handled entirely by _filter_by_occasion: if given,
        it tries an exact match first, then widens to progressively "less similar"
        occasions until a full outfit (top+bottom+shoes) is found, or signals
        failure if even the widest search has nothing.

        Gender/season/usage matching for bottoms+shoes (against the randomly
        picked top) is done via priority-ordered relaxation:
            1. gender + season + usage
            2. gender + usage            (season dropped)
            3. gender + season           (usage dropped)
            4. gender only               (season AND usage dropped)
            5. nothing                   (last resort)
        Gender is always required; usage outranks season, so season is dropped
        before usage when not everything can be satisfied at once.

        Returns a dict:
            {
              "top": ..., "bottom": ..., "shoes": ...,
              "occasion_requested": "Party" | ... | None,
              "occasion_matched_distance": 0/1/2/3/None,
              "occasion_exact": True/False/None
            }
        or None if the occasion is invalid, or no category (top/bottom/shoes)
        has any items even after the occasion search is fully widened.
        """
        if not self.top or not self.bottom or not self.shoes:
            raise ValueError("Add at least one top, bottom, and shoe")

        chosen_tops, chosen_bottoms, chosen_shoes, matched_distance = self._filter_by_occasion(usage)

        if chosen_tops is None:
            return None  # invalid occasion, or some category empty even at the widest search

        # Normalize usage the same way _filter_by_occasion did, so the returned
        # metadata reflects the actual occasion that was matched against.
        if usage is not None:
            usage_lookup = {u.lower(): u for u in VALID_USAGE}
            usage = usage_lookup.get(usage.strip().lower())

        top_item = random.choice(chosen_tops)

        gender = gender or top_item.get("gender")
        season = toseason or top_item.get("season")
        top_usage_for_matching = usage or top_item.get("usage")
        top_color = top_item.get("color_group")

        def item_matches(item, check_season, check_usage):
            """Gender is always required. Season/usage are checked only if requested."""
            if item["gender"] != gender and item["gender"] != "Unisex":
                return False
            if check_season and item["season"] != season:
                return False
            if check_usage and item["usage"] != top_usage_for_matching:
                return False
            return True

        # Priority-ordered relaxation: (check_season, check_usage) per step.
        relaxation_order = [
            (True, True),    # gender + season + usage
            (False, True),   # gender + usage            (season dropped)
            (True, False),   # gender + season           (usage dropped)
            (False, False),  # gender only
        ]

        matched_tier = None
        valid_combos = []
        for tier_index, (check_season, check_usage) in enumerate(relaxation_order):
            valid_combos = [
                (b, s) for b in chosen_bottoms for s in chosen_shoes
                if item_matches(b, check_season, check_usage) and item_matches(s, check_season, check_usage)
            ]
            if valid_combos:
                matched_tier = tier_index
                break

        # Absolute last resort: drop gender too, if even gender-only matched nothing
        if not valid_combos:
            valid_combos = [(b, s) for b in chosen_bottoms for s in chosen_shoes]
            matched_tier = 4  # last resort: no gender/season/usage filtering at all

        if not valid_combos:
            return None

        def color_score(a, b):
            dist = abs(a - b) % 9
            dist = min(dist, 9 - dist)
            if a in [9, 10, 11] or b in [9, 10, 11]:
                return 1.2
            return {0: 2.0, 1: 1.5, 2: 1.2, 3: 1.0, 4: 0.7, 5: 0.4}.get(dist, 0.2)

        recommended_bottom, recommended_shoe = find_combo_by_top(top_color, combotype)


        best_score = -1
        best_combo = None
        tied_best_combos = []

        for b, s in valid_combos:
            score = color_score(b["color_group"], recommended_bottom)
            score += color_score(s["color_group"], recommended_shoe)

            combo = {"top": top_item, "bottom": b, "shoes": s}

            if score > best_score:
                best_score = score
                tied_best_combos = [combo]
            elif score == best_score:
                tied_best_combos.append(combo)

        best_combo = random.choice(tied_best_combos)

        MATCH_QUALITY_LABELS = {
            0: "exact",   # gender + season + usage all matched
            1: "close",   # usage matched, season dropped
            2: "loose",   # season matched, usage dropped
            3: "weak",    # only gender matched
            4: "none",    # nothing filtered, pure color match
        }
        best_combo["match_tier"] = matched_tier
        best_combo["match_quality"] = MATCH_QUALITY_LABELS[matched_tier]
        best_combo["occasion_requested"] = usage
        best_combo["occasion_matched_distance"] = matched_distance
        best_combo["occasion_exact"] = (matched_distance == 0) if usage is not None else None


        return best_combo