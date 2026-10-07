from taravinyas_tamil_engine import lookup, DFA_STATE  # Import your dictionary module

def simulate_strokes(strokes):
    print("--- Starting Simulation ---")
    for stroke in strokes:
       try:
            result = lookup(stroke)
            print(f"Stroke: {str(stroke):<20} -> Emitted: '{result}'")
       except KeyError:
            print(f"Stroke: {str(stroke):<20} -> KEYERROR (Invalid Chord)")

# Test Case 1: Sequential typing
simulate_strokes([('S',)])     # Coarse
simulate_strokes([('J', 'K')])   # Fine
simulate_strokes([('V',)])        # Terminator

# Test Case 2: NKRO Single-Stroke
simulate_strokes([
    ('S', 'J', 'K', 'V')
])