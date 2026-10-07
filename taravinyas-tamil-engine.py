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

def flush_state():
    global DFA_STATE, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, EVAL_AS, XI
    DFA_STATE = "q0"
    ALPHA = 0
    BUFFER_COARSE = None
    BUFFER_FINE_EXTENDED = None
    EVAL_AS = None
    XI = 0

def is_coarse_or_extended(chord):
    check = sum(key in chord for key in 'FRDESW')
    if 'A' in chord and check == 0:
        return True
    elif check == 1:
        return False
    else:
        return None 


def extract_coarse_bits(chord):
    order = 'FRDESW';
    for key in order:
        idx = chord.find(key)
        if idx != -1:
            i = order.find(key)
            if i == 5:
                return [i, None]
            elif i > 2:
                return [i, i + 1]
            else:
                return [i, i]        


def is_fine_extended(chord):
    check = sum(key in chord for key in 'JUKIL') == 1

def extract_fine_extended_bits(chord):
    order = 'JUKIL';
    for key in order:
        idx = chord.find(key)
        if idx != -1:
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


def extract_terminators(chord):
    consonant = 'V' in chord
    standalone = 'X' in chord
    diacritic = 'C' in chord
    if consonant and (standalone or diacritic):
        return "INVALID"
    if standalone and diacritic:
        return "INVALID"
    if consonant:
        return "consonant"
    if standalone:
        return "vowel_standalone"
    if diacritic:
        return "vowel_diacritic"

def q0_phase(chord):
    global ALPHA, DFA_STATE, BUFFER_COARSE
        check = is_coarse_or_extended(chord)
        if check == 1: # Extended
            ALPHA = 1
            DFA_STATE = 'q2'
        elif check == 0: # Coarse
            ALPHA = 0
            BUFFER_COARSE = extract_coarse_bits(chord)
            DFA_STATE = 'q1' 
        else:
            flush_state()
            raise KeyError
        return ""


def q1_q2_phase(chord):
    global BUFFER_FINE_EXTENDED, DFA_STATE
        check = is_fine_extended(chord)
        if check:
            BUFFER_FINE_EXTENDED = extract_fine_extended_bits(chord)
            DFA_STATE = 'q3'
            return ""
        else:
            flush_state()
            raise KeyError

def q3_phase(chord):
    global EVAL_AS, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, XI
    EVAL_AS = extract_terminators(chord)
    character = ""
    if EVAL_AS == 'consonant': # q4: Consonant Terminator
        character = renderConsonant(ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED)
    elif EVAL_AS == 'vowel_standalone': # q5: Vowel (Standalone) Terminator
        XI = 0
        character = renderVowel(ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, XI)
    elif EVAL_AS == 'vowel_diacritic': # q5: Vowel (Diacritic) Terminator
        XI = 1
        character = renderVowel(ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, XI)
    else:
        flush_state()
        raise KeyError
    flush_state()
    if character == "INVALID":
        raise KeyError
    return character


def lookup(key):
    global DFA_STATE, ALPHA, BUFFER_COARSE, BUFFER_FINE_EXTENDED, EVAL_AS, XI
    chord = key[0]
    if DFA_STATE == 'q0':
        q0_phase(chord)
        if is_fine_extended(chord):
            q1_q2_phase(chord)
        if extract_terminators(chord) != "INVALID":
            return q3_phase(chord)
        return ""
    elif DFA_STATE == 'q1' or DFA_STATE == 'q2':
        q1_q2_phase(chord)
        if extract_terminators(chord) != "INVALID":
            return q3_phase(chord)
        return ""
    elif DFA_STATE == 'q3':
            return q3_phase(chord)
    else:
        flush_state()
        raise KeyError


def reverse_lookup(text):
    return []


def evaluate_consonants():
    if alpha == 