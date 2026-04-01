import streamlit as st
import pandas as pd
import time

# --- 1. Custom CSS for Uniform "Blue Graph" TV Look ---
st.markdown("""
<style>
    .stApp { background-color: #000033; }
    h3 {
        color: #FFCC00 !important;
        text-align: center;
        text-transform: uppercase;
        font-family: 'Arial Black', Gadget, sans-serif;
        text-shadow: 2px 2px #000000;
        min-height: 120px !important; 
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem !important;
        margin-bottom: 20px !important;
    }
    .stButton > button {
        background-color: #060ce9 !important;
        color: #FFCC00 !important;
        border: 3px solid #FFCC00 !important;
        height: 80px !important; /* Slightly shorter to fit 7 rows on screen */
        width: 100% !important;
        font-size: 24px !important;
        font-weight: bold !important;
        border-radius: 5px !important;
    }
    .stButton > button:hover {
        border-color: #FFFFFF !important;
        color: #FFFFFF !important;
    }
    .stButton > button:disabled {
        background-color: #000022 !important;
        color: #444444 !important;
        border: 2px solid #222222 !important;
    }
    .stTabs [data-baseweb="tab-list"] { background-color: #060ce9; padding: 10px; }
    .stTabs [data-baseweb="tab"] { color: white !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 2. Load Data from Music Manuscript ---
@st.cache_data
def load_data():
    return pd.DataFrame([
        # Theory
        {"Category": "Theory", "Points": 100, "Question": "A note that represents 1/4 of a beat.", "Answer": "What is a quarter note?"},
        {"Category": "Theory", "Points": 200, "Question": "A mark that means to gradually play louder.", "Answer": "What is a crescendo?"},
        {"Category": "Theory", "Points": 300, "Question": "The right hand symbol.", "Answer": "What is the treble clef?"},
        {"Category": "Theory", "Points": 400, "Question": "Playing rapidly between 2 notes.", "Answer": "What is a trill?"},
        {"Category": "Theory", "Points": 500, "Question": "The finale of a piece in the classical era.", "Answer": "What is a coda?"},
        # Composer
        {"Category": "Composer", "Points": 100, "Question": "This person composed their first piece at 5.", "Answer": "Who is Mozart?"},
        {"Category": "Composer", "Points": 200, "Question": "The most famous Polish Composer.", "Answer": "Who is Chopin?"},
        {"Category": "Composer", "Points": 300, "Question": "Credited with being Chopin's most famous rival.", "Answer": "Who is Liszt?"},
        {"Category": "Composer", "Points": 400, "Question": "This person is known as the father of music.", "Answer": "Who is Bach?"},
        {"Category": "Composer", "Points": 500, "Question": "This person taught Mozart the most.", "Answer": "Who is Leopold Mozart?"},
        # Famous Pieces
        {"Category": "Famous Pieces", "Points": 100, "Question": "Name the Piece (Visual/Audio cue)", "Answer": "Fur Elise - Beethoven"},
        {"Category": "Famous Pieces", "Points": 200, "Question": "Name the Piece (Visual/Audio cue)", "Answer": "Imperial March - John Williams"},
        {"Category": "Famous Pieces", "Points": 300, "Question": "Name the Piece (Visual/Audio cue)", "Answer": "Swan Lake - Tchaikovsky"},
        {"Category": "Famous Pieces", "Points": 400, "Question": "Name the Piece (Visual/Audio cue)", "Answer": "Claire de Lune - Debussy"},
        {"Category": "Famous Pieces", "Points": 500, "Question": "Name the Piece (Visual/Audio cue)", "Answer": "The British Grenadiers"},
        # Instruments
        {"Category": "Instruments", "Points": 100, "Question": "This instrument features 88 black and white keys.", "Answer": "What is a Piano?"},
        {"Category": "Instruments", "Points": 200, "Question": "This single-reed woodwind instrument is typically made of brass and is heavily featured in jazz.", "Answer": "What is a Saxophone?"},
        {"Category": "Instruments", "Points": 300, "Question": "This instrument is the smallest and highest-pitched member of the string family.", "Answer": "What is a Violin?"},
        {"Category": "Instruments", "Points": 400, "Question": "This stringed instrument provides the low-end frequencies in a band.", "Answer": "What is a bass?"},
        {"Category": "Instruments", "Points": 500, "Question": "This electronic musical instrument generates audio signals that can imitate other instruments.", "Answer": "What is a synth?"},
        # Play by Ear (Added 600 and 700)
        {"Category": "Play by Ear", "Points": 100, "Question": "What is the name of the song?", "Answer": "Last Carnival - Acoustic Cafe"},
        {"Category": "Play by Ear", "Points": 200, "Question": "What is the name of the song?", "Answer": "In the Hall of the Mountain King - Grieg"},
        {"Category": "Play by Ear", "Points": 300, "Question": "What is the name of the song?", "Answer": "Ballade No. 2 Coda - Chopin"},
        {"Category": "Play by Ear", "Points": 400, "Question": "What is the name of the song?", "Answer": "A Knife in the Dark - Howard Shore"},
        {"Category": "Play by Ear", "Points": 500, "Question": "What is the name of the song?", "Answer": "Victory - 2SFH"},
        {"Category": "Play by Ear", "Points": 600, "Question": "What is the name of the song?", "Answer": "Ludwig the Holy Blade - SIE Sound Team"},
        {"Category": "Play by Ear", "Points": 700, "Question": "What is the name of the song?", "Answer": "Davy Jones Suite - Hans Zimmer"}
    ])

df = load_data()
categories = df['Category'].unique()

# --- 3. Session State ---
if "players" not in st.session_state:
    st.session_state.update({
        "players": {}, "answered": [], "current_q": None, 
        "show_answer": False, "final_triggered": False, 
        "final_q_revealed": False, "final_a_revealed": False, "winner": None
    })

# --- 4. Sidebar ---
with st.sidebar:
    st.title("Host Admin")
    new_p = st.text_input("Player Name")
    if st.button("Add Player") and new_p:
        st.session_state.players[new_p] = 0
        st.rerun()
    st.divider()
    if not st.session_state.final_triggered:
        if st.button("🔥 FINAL JEOPARDY", type="primary"):
            st.session_state.final_triggered = True
            st.rerun()
    else:
        if st.button("↩️ BOARD"):
            st.session_state.final_triggered = False
            st.session_state.final_q_revealed = False
            st.session_state.final_a_revealed = False
            st.rerun()
    if st.button("Reset All"):
        st.session_state.clear()
        st.rerun()

# --- 5. Tabs ---
tab1, tab2 = st.tabs(["🎮 GAME BOARD", "🏆 LEADERBOARD"])

with tab1:
    if st.session_state.winner:
        st.balloons()
        st.title(f"🥇 THE WINNER IS {st.session_state.winner.upper()}!")
        if st.button("Back to Game"):
            st.session_state.winner = None
            st.rerun()

    elif st.session_state.final_triggered:
        st.title("🏆 FINAL JEOPARDY")
        st.markdown("### Category: Music History")
        
        if not st.session_state.final_q_revealed:
            if st.button("REVEAL FINAL QUESTION", use_container_width=True):
                st.session_state.final_q_revealed = True
                st.rerun()
        
        if st.session_state.final_q_revealed:
            st.warning("### Name the 4 Time Periods of Music.")
            
            if not st.session_state.final_a_revealed:
                if st.button("REVEAL FINAL ANSWER"):
                    st.session_state.final_a_revealed = True
                    st.rerun()
            
            if st.session_state.final_a_revealed:
                st.success("### Answer: Baroque, Classical, Romantic, Modern")
                st.balloons()
    
    elif st.session_state.current_q is None:
        cols = st.columns(len(categories))
        for i, cat in enumerate(categories):
            with cols[i]:
                st.markdown(f"### {cat}")
                cat_qs = df[df['Category'] == cat].sort_values('Points')
                for _, row in cat_qs.iterrows():
                    q_id = f"{cat}-{row['Points']}"
                    if q_id in st.session_state.answered:
                        st.button("X", key=q_id, disabled=True)
                    else:
                        if st.button(f"${row['Points']}", key=q_id):
                            st.session_state.current_q = row
                            st.rerun()
    else:
        q = st.session_state.current_q
        st.info(f"{q['Category']} - ${q['Points']}")
        st.markdown(f"## {q['Question']}")
        
        if not st.session_state.show_answer:
            if st.button("REVEAL ANSWER", use_container_width=True):
                st.session_state.show_answer = True
                st.rerun()
        else:
            st.success(f"### {q['Answer']}")
            st.write("---")
            st.write("### Assign Points")
            p_cols = st.columns(max(len(st.session_state.players), 1))
            for i, name in enumerate(st.session_state.players):
                col_correct, col_wrong = p_cols[i].columns(2)
                if col_correct.button("✅", key=f"c_{name}"):
                    st.session_state.players[name] += q['Points']
                    st.balloons()
                    time.sleep(1) 
                    st.session_state.answered.append(f"{q['Category']}-{q['Points']}")
                    st.session_state.current_q, st.session_state.show_answer = None, False
                    st.rerun()
                if col_wrong.button("❌", key=f"w_{name}"):
                    st.session_state.players[name] -= q['Points']
                    st.snow()
                    time.sleep(1)
                    st.rerun()
            if st.button("Skip Question"):
                st.session_state.answered.append(f"{q['Category']}-{q['Points']}")
                st.session_state.current_q, st.session_state.show_answer = None, False
                st.rerun()

with tab2:
    st.header("Current Rankings")
    if st.session_state.players:
        sorted_p = dict(sorted(st.session_state.players.items(), key=lambda item: item[1], reverse=True))
        for name, score in sorted_p.items():
            c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 1.5])
            c1.markdown(f"## {name}")
            c2.markdown(f"## ${score}")
            if c3.button("+$100", key=f"add_{name}"): st.session_state.players[name] += 100; st.rerun()
            if c4.button("-$100", key=f"sub_{name}"): st.session_state.players[name] -= 100; st.rerun()
            if c5.button("🏆 WINNER", key=f"win_{name}"):
                st.session_state.winner = name
                st.rerun()
            st.divider()
    else:
        st.info("Add players in the sidebar to start.")