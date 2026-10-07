LONGEST_KEY = 1
# State persists between strokes because Plover keeps the script loaded in memory
DFA_STATE = "q0"
ALPHA = 0
BUFFER_COARSE = None
BUFFER_FINE_EXTENDED = None
EVAL_AS = None
XI = 0

VOWEL_LOOKUP_TABLE = [
   ["அ", "இ", "உ", "எ", "ஒ"],
   ["ஆ", "ஈ", "ஊ", "ஏ", "ஓ"],
   [None, None, None, "ஐ", "ஔ"],
   None,
   ["", "\u0BBF", "\u0BC1", "\u0BC6", "\u0BCA"],
   ["\u0BBE", "\u0BC0", "\u0BC2", "\u0BC7", "\u0BCB"],
   [None, None, None, "\u0BC8", "\u0BCC"],
   "INVALID",
   "\u0BCD",
   "\u0B83",
   "\u200C",
   None,
   None,
   None,
   None,
   None,
];

CONSONANT_LOOKUP_TABLE = [
    ["க", "ச", "ட", "த", "ப", "ற"],
    ["ங", "ஞ", "ண", "ந", "ம", "ன"],
    [None, "ய", "ழ", None, "வ", "ர"],
    [None, None, "ள", None, None, "ல"],
    [None, "ஶ", "ஷ", None, None, "ஸ"],
    None,
    None,
    "INVALID",
    "ஜ",
    "ஹ",
    "க்ஷ",
    None,
    None,
    None,
    None,
    None,
];

# Used to fully flush and reset the global variables.
# For raising error mid-process, 
# passing raise_error=True keeps code clean.
def flush_state(raise_error):
    global DFA_STATE, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, EVAL_AS, XI
    DFA_STATE = "q0"
    ALPHA = 0
    BUFFER_COARSE = None
    BUFFER_FINE_EXTENDED = None
    EVAL_AS = None
    XI = 0
    if raise_error is True:
        raise KeyError

# Are we pressing a coarse key (False), the extended mode key (True), or something else (None)?
def is_coarse_or_extended(chord):
    check = sum(key in chord for key in 'FRDESW')
    if 'A' in chord and check == 0:
        return False # Extended
    elif check == 1:
        return True # Coarse
    else:
        return None # Neither

# Used to extract the coarse bit.
# Use is_coarse_or_extended() before passing here.
# Code is strictly for a single coarse key per chord
# Format: [Consonant, Vowel]
def extract_coarse_bits(chord):
    order = 'FRDESW';
    for key in order:
        i = order.index(key)
        if i == 5:
            return [i, None]
        elif i > 2:
            return [i, i + 1]
        else:
            return [i, i]        

# Are we pressing keys for fine positions/extended character positions? (bool)
def is_fine_extended(chord, alpha):
    if alpha == 0:
        keys = 'JUKIL'
    else:
        keys = 'JUK'
    check = sum(key in chord for key in keys)
    if check > 1:
        return None
    elif check == 1:
        return True
    else:
        return False

# Used to extract the fine/extended bits.
# Use is_fine_extended()  before passing here.
# Code is strictly for a single fine/extended key per chord
def extract_fine_extended_bits(chord, alpha):
    if alpha == 0:
        order = 'JUKIL';
    else:
        order = 'JUK';
    for key in order:
        idx = chord.index(key)
        if alpha == 0:
            if key == 'J':
                return 0b00001
            elif key == 'U':
                return 0b00010
            elif key == 'K':
                return 0b00100
            elif key == 'I':
                return 0b01100
            elif key == 'L':
                return 0b10000
        else:
            if key == 'J':
                return 0b00
            elif key == 'U':
                return 0b01
            elif key == 'K':
                return 0b10


# Do we want to render it as a consonant, a diacritic, or a standalone vowel? Or is the rendering method not clear?
def extract_terminators(chord):
    consonant = 'V' in chord
    standalone = 'X' in chord
    diacritic = 'C' in chord
    if not (consonant or standalone or diacritic):
        return "nothing"
    if consonant and (standalone or diacritic):
        return "INVALID"
    if standalone and diacritic:
        return "vowel_extended"
    if consonant:
        return "consonant"
    if standalone:
        return "vowel_standalone"
    if diacritic:
        return "vowel_diacritic"
    else:
        return "INVALID"

# Transition from q0: Take the coarse keys / extended mode
def q0_phase(chord):
    global ALPHA, DFA_STATE, BUFFER_COARSE
    check = is_coarse_or_extended(chord)
    if check is True: # Coarse
        ALPHA = 0
        BUFFER_COARSE = extract_coarse_bits(chord)
        DFA_STATE = 'q1' 
    elif check is False: # Extended
        ALPHA = 1
        DFA_STATE = 'q2'

# Transition from q1 & q2: Take the fine/extended mode keys
def q1_q2_phase(chord):
    global BUFFER_FINE_EXTENDED, DFA_STATE, ALPHA
    check = is_fine_extended(chord, ALPHA)
    if check is True:
       BUFFER_FINE_EXTENDED = extract_fine_extended_bits(chord, ALPHA)
       DFA_STATE = 'q3'
    elif check is None:
       flush_state(True)
    else:
        DFA_STATE = 'q3'


# Transition from q3: Find terminators and render consonant
def q3_phase(chord):
    global EVAL_AS, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, XI
    EVAL_AS = extract_terminators(chord)
    character = ""
    if EVAL_AS == 'consonant': # q4: Consonant Terminator
        print(ALPHA, BUFFER_COARSE[0], BUFFER_FINE_EXTENDED)
    elif EVAL_AS == 'vowel_standalone': # q5: Vowel (Standalone) Terminator
        XI = 0 # not relevant when Alpha = 1
        print(ALPHA, BUFFER_COARSE[1], BUFFER_FINE_EXTENDED, XI)
    elif EVAL_AS == 'vowel_diacritic': # q5: Vowel (Diacritic) Terminator
        XI = 1 # not relevant when Alpha = 1
        print(ALPHA, BUFFER_COARSE[1], BUFFER_FINE_EXTENDED, XI)
    elif EVAL_AS == 'vowel_extended': 
        print(ALPHA, BUFFER_FINE_EXTENDED)
    elif EVAL_AS == 'INVALID':
        flush_state(True)
    flush_state(False)
    if character == "INVALID":
        raise KeyError
    return character

def lookup(key):
    global DFA_STATE, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, EVAL_AS, XI
    chord = key[0]
    print(DFA_STATE, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, EVAL_AS, XI)
    if DFA_STATE == 'q0':
        print("q0")
        q0_phase(chord)
        print(is_fine_extended(chord, ALPHA))
        if is_fine_extended(chord, ALPHA) is None:
            flush_state(True)
        elif is_fine_extended(chord, ALPHA) is True:
            print("q1/q2")
            q1_q2_phase(chord)
            print(extract_terminators(chord))
            if extract_terminators(chord) == "INVALID":
                flush_state(True)
            elif extract_terminators(chord) != "nothing":
                print("q3")
                return q3_phase(chord)
        return ""
    elif DFA_STATE == 'q1' or DFA_STATE == 'q2':
        q1_q2_phase(chord)
        print(extract_terminators(chord))
        if extract_terminators(chord) == "INVALID":
            flush_state(True)
        else:
            print("q3")
            return q3_phase(chord)
        return ""
    elif DFA_STATE == 'q3':
            return q3_phase(chord)
    else:
        flush_state(True)


def reverse_lookup(text):
    return []
