import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
import time

# --- AUTHENTICATION MODULE ---
def check_password():
    """Returns `True` if the user had the correct password."""
    # 1. If no password set in secrets, allow access (Demo Mode or Local Dev)
    if "APP_PASSWORD" not in st.secrets:
        return True

    # 2. Check session state
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    # 3. Password Input
    st.markdown("## 🔒 Ezzenzo OS")
    st.markdown("System access is restricted.")
    pwd = st.text_input("Enter Access Code", type="password")
    
    if st.button("Login"):
        if pwd == st.secrets["APP_PASSWORD"]:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("⛔ Access Denied")
            
    return False

# Try to import Google integrations; handle gracefully if not configured yet
try:
    from streamlit_gsheets import GSheetsConnection
    import google.generativeai as genai
    HAS_INTEGRATIONS = True
except ImportError:
    HAS_INTEGRATIONS = False

# --- 1. CONFIGURATION & STATE ---
st.set_page_config(
    page_title="Ezzenzo OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for "Premium/Dark" aesthetic
st.markdown("""
    <style>
    /* Global Font & Colors */
    .stApp { background-color: #0e1117; color: #fafafa; }
    h1, h2, h3 { font-family: 'Helvetica Neue', sans-serif; font-weight: 300; letter-spacing: -0.5px; }
    
    /* Metrics Cards */
    div[data-testid="stMetric"] {
        background-color: #262730;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #7c3aed; /* Ezzenzo Purple */
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: 500;
        height: 3em;
        background-color: #262730;
        border: 1px solid #4b5563;
        color: white;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        border-color: #7c3aed;
        color: #7c3aed;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA MANAGER (HANDLES MOCK VS REAL) ---
class DataManager:
    def __init__(self):
        # Check if secrets exist to determine mode
        self.use_real_data = "connections" in st.secrets and "gsheets" in st.secrets["connections"]
        self.api_ready = "GEMINI_API_KEY" in st.secrets
        
        if self.api_ready:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

    def get_finance_data(self):
        if self.use_real_data:
            conn = st.connection("gsheets", type=GSheetsConnection)
            try:
                return conn.read(worksheet="Transactions", ttl=60)
            except:
                st.warning("⚠️ Could not read 'Transactions' tab. Using mock data.")
        
        # Mock Data
        return pd.DataFrame([
            {"Date": "2024-02-01", "Category": "Raw Materials", "Amount": -450, "Type": "Expense", "Project": "Scent Lab"},
            {"Date": "2024-02-03", "Category": "Ad Revenue", "Amount": 1200, "Type": "Income", "Project": "Silent Relics"},
            {"Date": "2024-02-05", "Category": "Software Sub", "Amount": -30, "Type": "Expense", "Project": "System"},
            {"Date": "2024-02-06", "Category": "Sponsorship", "Amount": 850, "Type": "Income", "Project": "StillWatchn"},
        ])

    def get_scent_data(self):
        if self.use_real_data:
            conn = st.connection("gsheets", type=GSheetsConnection)
            try:
                return conn.read(worksheet="Blends", ttl=0)
            except:
                 st.warning("⚠️ Could not read 'Blends' tab.")
        
        return pd.DataFrame([
            {"Date": "2024-01-20", "Blend_Name": "Midnight Asphalt", "Version": "1.2", "Target_Vibe": "Industrial", "Rating": 4},
            {"Date": "2024-02-02", "Blend_Name": "Velvet Rain", "Version": "2.0", "Target_Vibe": "Atmospheric", "Rating": 5},
        ])

    def log_scent_test(self, data_dict):
        if self.use_real_data:
            conn = st.connection("gsheets", type=GSheetsConnection)
            try:
                # Simple append logic (requires reading full sheet first in Streamlit GSheets)
                df = conn.read(worksheet="Blends")
                new_row = pd.DataFrame([data_dict])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="Blends", data=updated_df)
                return True
            except Exception as e:
                st.error(f"Save failed: {e}")
                return False
        else:
            # Simulate save
            time.sleep(1)
            return True

    def generate_ai_text(self, prompt):
        if self.api_ready:
            try:
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"⚠️ API Error: {str(e)}"
        else:
            time.sleep(1.5)
            return "🔒 [DEMO MODE] This would be a real AI response generated by Gemini. Configure secrets.toml to enable live generation."

# Initialize Data Manager
dm = DataManager()

# --- 3. UI COMPONENTS ---

def render_sidebar():
    st.sidebar.title("Ezzenzo OS")
    st.sidebar.caption(f"Status: {'🟢 Connected' if dm.use_real_data else '🟡 Demo Mode'}")
    
    menu = st.sidebar.radio(
        "Navigation", 
        ["🏠 Command Centre", "🎬 Content Studio", "🧪 Scent Lab", "💰 Finance", "📊 Performance"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Quick Links")
    st.sidebar.link_button("Go to Veo (Video)", "https://gemini.google.com/app")
    st.sidebar.link_button("Go to Sheets", "https://docs.google.com")
    
    return menu

def render_home():
    st.title("Command Centre")
    st.markdown("### Weekly Snapshot")
    
    df_fin = dm.get_finance_data()
    income = df_fin[df_fin['Type']=='Income']['Amount'].sum()
    expense = df_fin[df_fin['Type']=='Expense']['Amount'].sum()
    
    # 1. Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Weekly Output", "3 Packs", "+1 vs avg")
    c2.metric("Scent Tests", "5 Blends", "Active")
    c3.metric("Net Profit (MTD)", f"${income+expense}", f"{((income+expense)/100):.1f}%")
    c4.metric("Pending Renders", "2 Videos", "Urgent")

    # 2. Action Tiles
    st.markdown("### ⚡ Quick Actions")
    ac1, ac2, ac3, ac4 = st.columns(4)
    
    with ac1:
        if st.button("🎬 Silent Relics Batch"):
            st.session_state['nav_override'] = "🎬 Content Studio"
            st.rerun()
    with ac2:
        if st.button("🎬 StillWatchn Batch"):
            st.session_state['nav_override'] = "🎬 Content Studio"
            st.rerun()
    with ac3:
        if st.button("🧪 Log Scent Test"):
            st.session_state['nav_override'] = "🧪 Scent Lab"
            st.rerun()
    with ac4:
        if st.button("💰 Log Expense"):
            st.session_state['nav_override'] = "💰 Finance"
            st.rerun()

    # 3. Next Actions Feed
    st.markdown("### 🧠 Smart Feed")
    feed_col, _ = st.columns([2, 1])
    with feed_col:
        st.info("⚠️ **Silent Relics:** 'Chernobyl Roof' script is approved but needs Veo rendering.")
        st.warning("⚠️ **Finance:** Raw Materials category is 15% over budget this month.")
        st.success("✅ **Scent Lab:** 'Velvet Rain' v2.0 received a 5/5 rating. Ready for scaling?")

def render_content_studio():
    st.title("Content Studio")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Batch Builder", "📂 Pack Viewer", "💾 Asset Library"])
    
    # --- BATCH BUILDER ---
    with tab1:
        st.subheader("Generate New Content Batch")
        c1, c2 = st.columns([1, 2])
        
        with c1:
            with st.form("batch_gen"):
                channel = st.radio("Channel", ["Silent Relics (Dark History)", "StillWatchn (Micro-Horror)"])
                count = st.slider("Quantity", 1, 5, 3)
                context = st.text_input("Specific Focus (Optional)", placeholder="e.g. Victorian Medicine")
                submit_batch = st.form_submit_button("🚀 Generate Concepts")
        
        with c2:
            if submit_batch:
                with st.spinner("Gemini is brainstorming..."):
                    prompt = f"Generate {count} short-form video concepts for '{channel}'. Focus: {context}. Return as a bulleted list with hooks."
                    ideas = dm.generate_ai_text(prompt)
                    st.success("Draft Concepts Generated")
                    st.markdown(ideas)
                    st.button("Save to Library", key="save_ideas")

    # --- PACK VIEWER ---
    with tab2:
        st.subheader("Active Packs")
        
        # Mock Pack Data
        pack = {
            "title": "The Molasses Flood",
            "hook": "Imagine a wave of syrup killing 21 people. It happened in 1919.",
            "img_prompt": "Cinematic, photorealistic, 1919 Boston street, flooding with dark viscous liquid, steam rising, panic, 9:16 aspect ratio",
            "vid_prompt": "Dark viscous liquid flooding a cobblestone street, steam rising, night time, cinematic lighting, 4k"
        }
        
        st.markdown(f"**Current Project:** {pack['title']}")
        
        col_script, col_prompts = st.columns(2)
        
        with col_script:
            st.caption("SCRIPT")
            script_text = st.text_area("Edit Script", value=f"HOOK: {pack['hook']}\n\nSCENE 1: [Visual: Old Boston photo] Narration: It wasn't water. It was molasses.\n\nSCENE 2: ...", height=300)
            if st.button("✨ AI Rewrite Hook"):
                new_hook = dm.generate_ai_text(f"Rewrite this hook to be more viral and shocking: {pack['hook']}")
                st.info(new_hook)

        with col_prompts:
            st.caption("GENERATION PROMPTS (Copy to Gemini/Veo)")
            st.text_input("Image Prompt (Nano Banana)", value=pack['img_prompt'])
            st.text_input("Video Prompt (Veo)", value=pack['vid_prompt'])
            st.info("💡 Copy these prompts, generate in Gemini, then upload results to the Asset Library.")

    # --- ASSET LIBRARY ---
    with tab3:
        st.subheader("Asset Storage")
        st.file_uploader("Upload Generated Files (MP4/PNG)", accept_multiple_files=True)
        st.image("https://placehold.co/600x400/262730/white?text=Preview+Gallery", caption="Recent Generations")

def render_scent_lab():
    st.title("Scent Lab")
    
    t1, t2 = st.tabs(["⚗️ Blend Testing", "📦 Inventory"])
    
    with t1:
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("Log New Test")
            with st.form("scent_test"):
                name = st.text_input("Blend Name")
                ver = st.text_input("Version (e.g. 1.2)")
                vibe = st.text_input("Target Vibe")
                formula = st.text_area("Formula (Drops/Grams)")
                notes = st.text_area("Sensory Notes (0m / 10m / 1h)")
                rating = st.slider("Rating", 1, 5, 3)
                
                submitted = st.form_submit_button("🧪 Analyze & Save")
        
        with c2:
            st.subheader("AI Perfumer Feedback")
            if submitted:
                with st.spinner("Analyzing chemical balance..."):
                    # Save Logic
                    data = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Blend_Name": name, "Version": ver,
                        "Formula": formula, "Testing_Notes": notes, "Rating": rating
                    }
                    saved = dm.log_scent_test(data)
                    
                    if saved:
                        st.success(f"Logged {name} v{ver}")
                        # AI Logic
                        prompt = f"Act as a master perfumer. Analyze this formula: {formula}. User notes: {notes}. Target Vibe: {vibe}. Suggest one specific improvement."
                        feedback = dm.generate_ai_text(prompt)
                        st.markdown(feedback)
            
            st.divider()
            st.subheader("Recent Tests")
            st.dataframe(dm.get_scent_data(), use_container_width=True)

    with t2:
        st.subheader("Raw Materials")
        # In real mode, this would be editable
        inv_data = pd.DataFrame([
             {"Ingredient": "Bergamot Reggio", "Type": "Top", "Stock %": 80, "Supplier": "Eden"},
             {"Ingredient": "Iso E Super", "Type": "Base", "Stock %": 40, "Supplier": "PA"},
             {"Ingredient": "Oud Assafi", "Type": "Base", "Stock %": 10, "Supplier": "Firmenich"},
        ])
        st.data_editor(inv_data, use_container_width=True)

def render_finance():
    st.title("Finance Dashboard")
    
    df = dm.get_finance_data()
    
    # Financial Overview
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("Cash Flow")
        # Ensure numeric
        df['Amount'] = pd.to_numeric(df['Amount'])
        fig = px.bar(df, x='Date', y='Amount', color='Type', title="Income vs Expenses", color_discrete_map={"Income": "#00CC96", "Expense": "#EF553B"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Breakdown")
        pie = px.pie(df, values=df['Amount'].abs(), names='Category', hole=0.4)
        pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(pie, use_container_width=True)

    # Add Transaction Form
    with st.expander("➕ Add New Transaction", expanded=False):
        with st.form("add_trans"):
            dc1, dc2, dc3 = st.columns(3)
            date = dc1.date_input("Date")
            typ = dc2.selectbox("Type", ["Expense", "Income"])
            cat = dc3.selectbox("Category", ["Raw Materials", "Software", "Hardware", "Ads", "Sales"])
            amt = st.number_input("Amount ($)", step=0.01)
            proj = st.selectbox("Project", ["Ezzenzo Scents", "Silent Relics", "StillWatchn", "General"])
            
            if st.form_submit_button("Save to Sheets"):
                # In real mode, this would write to sheets using dm.log_transaction
                st.success(f"Logged ${amt} for {cat}")

def render_performance():
    st.title("Performance Tracker")
    st.info("Connect YouTube/TikTok APIs in Phase 2 for automatic tracking.")
    
    # Manual Tracker
    st.subheader("Video Log")
    
    video_data = pd.DataFrame([
        {"Title": "The Dancing Plague", "Views": 15400, "Likes": 1200, "Retention": "65%", "Platform": "TikTok"},
        {"Title": "Chernobyl Roof", "Views": 450, "Likes": 20, "Retention": "40%", "Platform": "YouTube Shorts"},
    ])
    
    edited_df = st.data_editor(video_data, num_rows="dynamic", use_container_width=True)
    
    if st.button("Update Metrics"):
        st.toast("Metrics saved to database")

# --- 4. MAIN CONTROLLER ---

def main():
    # SECURITY CHECK
    if not check_password():
        st.stop()

    # Handle Navigation Override (from Home Screen buttons)
    if 'nav_override' in st.session_state:
        selection = st.session_state['nav_override']
        del st.session_state['nav_override'] # Clear it after use
    else:
        selection = render_sidebar()

    # Router
    if "Home" in selection:
        render_home()
    elif "Content Studio" in selection:
        render_content_studio()
    elif "Scent Lab" in selection:
        render_scent_lab()
    elif "Finance" in selection:
        render_finance()
    elif "Performance" in selection:
        render_performance()

if __name__ == "__main__":
    main()
