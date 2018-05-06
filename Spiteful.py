''' 
Spiteful Summoner Probability Calculator 1.0 

Mulligan strategy: mulligan away any non-Spiteful cards

Assumptions:
- No blacklisting: it's possible to get back a mulliganed card (I know this is not the case, but I'm
  making this assumption anyway because otherwise it would be much harder to compute the exact
  probabilities; also, it can change the mulligan strategy to something more complex, e.g. keep all
  Spiteful Summoners and all spells that cost less than 3 mana)
'''

# Number of spells and Spiteful summoners in deck; change it to whatever you want.
spiteful_total = 2
spells_total = [
    0,    # number of 0-mana spells
    0,    # number of 1-mana spells
    0,    # 2
    0,    # 3
    0,    # 4
    0,    # 5
    0,    # 6
    0,    # 7
    0,    # 8
    0,    # 9
    2,    # 10
]
deck_size = 30
n_cards = 10
move_first = True

print("Deck Settings")
print("Number of Spiteful Summoner in deck: {}".format(spiteful_total))
print("Number of spells in deck:")
for mana_cost, count in enumerate(spells_total):
  print("{} mana: {} cards".format(mana_cost, count))
print("")

from copy import deepcopy

def P(n):
    # Compute factorial(n)
    f = 1.0
    for i in range(1, n+1):
        f *= i
    return f

def nCr(n, k):
    # Compute n choose k (combination)
    if k > n: return 0.0
    return P(n) / (P(k) * P(n - k))

def spiteful_probabilities(n_cards=4, move_first=True):
    # Compute the probability of drawing 0, 1, or 2 Spiteful Summoners after drawing n_cards,
    # as well as the expected distribution of spells remaining in the deck after drawing n_cards
    
    # Pre-mulligan phase
    spiteful_probs = []
    starting_hand_size = 3 if move_first else 4
    for starting_spiteful in range(spiteful_total+1):
        prob = nCr(spiteful_total, starting_spiteful)                * nCr(deck_size - spiteful_total, starting_hand_size - starting_spiteful)                / nCr(deck_size, starting_hand_size)
        spiteful_probs.append(prob)
    
    # Mulligan phase
    new_spiteful_probs = [0.0] * len(spiteful_probs)
    for spiteful_count, prob in enumerate(spiteful_probs):
        mulligan_count = starting_hand_size - spiteful_count
        for new_spiteful_count in range(spiteful_count, spiteful_total+1):
            spiteful_diff = new_spiteful_count - spiteful_count
            spiteful_remaining = spiteful_total - spiteful_count
            new_prob = nCr(spiteful_remaining, spiteful_diff)                        * nCr(deck_size - starting_hand_size - spiteful_remaining, mulligan_count - spiteful_diff)                        / nCr(deck_size - starting_hand_size, mulligan_count)
            new_spiteful_probs[new_spiteful_count] += prob * new_prob
    
    # Post-mulligan phase
    # Compute the probability of drawing 0, 1, or 2 Spiteful Summoners after drawing n_cards
    drawn_cards = starting_hand_size
    while drawn_cards < n_cards:
        # Draw a card
        spiteful_probs = deepcopy(new_spiteful_probs)
        new_spiteful_probs = [0.0] * len(spiteful_probs)
        
        for spiteful_count, prob in enumerate(spiteful_probs):
            spiteful_remaining = spiteful_total - spiteful_count
            cards_remaining = deck_size - drawn_cards
            draw_spiteful_prob = spiteful_remaining / cards_remaining
            # Does not draw Spiteful
            new_spiteful_probs[spiteful_count] += prob * (1.0 - draw_spiteful_prob)
            # Draws Spiteful
            if spiteful_count < spiteful_total:
                new_spiteful_probs[spiteful_count+1] += prob * draw_spiteful_prob
            
        drawn_cards += 1
    spiteful_probs = deepcopy(new_spiteful_probs)
        
    # Compute expected distribution of spells remaining in the deck after drawing n_cards
    expected_spells = [[0.0 for _ in range(max(spells_total)+1)] for _ in range(len(spells_total))]
    for spiteful_count, prob in enumerate(spiteful_probs):
        non_spiteful_draws = n_cards - spiteful_count
        non_spiteful_count = deck_size - spiteful_count
        for m in range(len(spells_total)):
            for c in range(min(non_spiteful_draws, spells_total[m])+1):
                # Compute probability of having exactly c m-mana spells in the deck after
                # drawing non_spiteful_draws cards
                c_complement = spells_total[m] - c
                spells_prob = nCr(spells_total[m], c_complement)                               * nCr(non_spiteful_count - spells_total[m], non_spiteful_draws - c_complement)                               / nCr(non_spiteful_count, non_spiteful_draws)
                expected_spells[m][c] += prob * spells_prob
    
    return new_spiteful_probs, expected_spells

spiteful_probs, expected_spells = spiteful_probabilities(n_cards=n_cards, move_first=move_first)

dud_prob = 0.0
def compute_expected_summon():
    spell_count = [0] * len(spells_total)
    expected_summon = [0.0] * len(spells_total)
    expected_summon_dfs(0, spell_count, 1.0, expected_summon)
    return expected_summon

def expected_summon_dfs(m, spell_count, total_prob, expected_summon):
    if m > 10:
        total_spells = sum(spell_count)
        if total_spells == 0:
            global dud_prob
            dud_prob = total_prob
        else:
            for mana_cost in range(11):
                expected_summon[mana_cost] += total_prob * spell_count[mana_cost] / total_spells
        return
    
    for c, prob in enumerate(expected_spells[m]):
        if prob < 1e-7: continue  # ignore impossible cases
        spell_count[m] += c
        expected_summon_dfs(m + 1, spell_count, total_prob * prob, expected_summon)
        spell_count[m] -= c

expected_summon = compute_expected_summon()

decimal_places = 3
print("Probability of drawing Spiteful Summoner within the first {} cards:".format(n_cards))
for spiteful_count, prob in enumerate(spiteful_probs):
    print("{} copies: {}".format(spiteful_count, round(prob, decimal_places)))
print("")
print("Expected distribution of spells remaining in the deck after drawing {} cards:".format(n_cards))
for mana_cost, expected_m in enumerate(expected_spells):
    print("{} mana: ".format(mana_cost), end="")
    for spell_count, prob in enumerate(expected_m):
        print("({}, {})".format(spell_count, round(prob, decimal_places)), end=" ")
    print("")
print("")
print("Expected outcomes of playing Spiteful Summoner at this turn:")
print("Dud:", round(dud_prob, decimal_places))
for mana_cost, prob in enumerate(expected_summon):
    print("{} mana: {}".format(mana_cost, round(prob, decimal_places)))

