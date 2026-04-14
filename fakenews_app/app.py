import streamlit as st
import os
import pandas as pd
import plotly.express as px

# Must be the first Streamlit command
st.set_page_config(
    page_title="Fake News Detection Tool",
    page_icon=None,
    layout="centered"
)

from utils.logger import get_logger
from utils.helpers import format_confidence
from services.preprocess import clean_text
from services.claim_extractor import extract_claims
from models.classifier import classify_text
from services.explain import explain_prediction
from services.source_checker import check_source_trust
from services.factcheck import fact_check_claims, get_api_key
from services.admin_manager import log_analysis, load_sources, add_source, remove_source, get_logs, get_analytics
from services.feedback_manager import save_feedback, load_feedback

logger = get_logger(__name__)

def inject_custom_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Inter', sans-serif;
            }

            .main, .stApp {
                background-color: #F9FAFB;
            }

            .card {
                background-color: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 15px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }

            .title-h1 {
                text-align: center;
                font-size: 2.2rem;
                font-weight: 700;
                color: #111827;
                margin-bottom: 0.2rem;
            }

            .subtitle {
                text-align: center;
                font-size: 1.05rem;
                color: #6b7280;
                margin-bottom: 2rem;
            }

            div[data-baseweb="textarea"] > div, div[data-baseweb="input"] > div {
                background-color: #ffffff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
            }

            div.stButton > button:first-child {
                background-color: #2563EB;
                color: white;
                width: 100%;
                height: 3rem;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1.05rem;
                border: none;
                transition: background-color 0.2s ease, box-shadow 0.2s ease;
                box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2), 0 2px 4px -1px rgba(37, 99, 235, 0.1);
            }

            div.stButton > button:first-child:hover {
                background-color: #1d4ed8;
                color: white;
            }

            .box-prediction-real {
                background-color: #dcfce7;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #16A34A;
                margin-bottom: 1rem;
            }

            .box-prediction-fake {
                background-color: #fee2e2;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #DC2626;
                margin-bottom: 1rem;
            }

            .box-prediction-uncertain {
                background-color: #fef9c3;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #eab308;
                margin-bottom: 1rem;
            }

            .box-claims {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                margin-bottom: 1rem;
            }

            .box-explanation {
                background-color: #eff6ff;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2563EB;
                margin-bottom: 1rem;
            }

            .box-source-trusted {
                background-color: #dcfce7;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #16A34A;
                margin-bottom: 1rem;
            }

            .box-source-untrusted {
                background-color: #fee2e2;
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #DC2626;
                margin-bottom: 1rem;
            }
            
            .box-factcheck {
                background-color: white;
                padding: 15px;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                margin-bottom: 1rem;
            }

            .box-label {
                font-size: 0.8rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
                color: #6b7280;
                margin-bottom: 0.5rem;
            }

            .custom-footer {
                text-align: center;
                color: #9ca3af;
                font-size: 0.85rem;
                margin-top: 3rem;
                padding-bottom: 2rem;
                border-top: 1px solid #e5e7eb;
                padding-top: 1.5rem;
            }
        </style>
    """, unsafe_allow_html=True)


def init_session_state():
    if "is_admin_authenticated" not in st.session_state:
        st.session_state.is_admin_authenticated = False
    if "admin_api_key" not in st.session_state:
        st.session_state.admin_api_key = ""
    if "has_results" not in st.session_state:
        st.session_state.has_results = False
    if "results" not in st.session_state:
        st.session_state.results = {}
    if "show_feedback_form" not in st.session_state:
        st.session_state.show_feedback_form = False

def admin_login():
    st.subheader("Admin Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            if username == "admin" and password == "admin123":
                st.session_state.is_admin_authenticated = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid credentials.")

def render_admin_dashboard():
    st.title("Admin Dashboard")

    if not st.session_state.is_admin_authenticated:
        admin_login()
        return

    def do_logout():
        st.session_state.is_admin_authenticated = False

    st.sidebar.button("Logout", on_click=do_logout)

    tab1, tab2, tab3, tab4 = st.tabs(["API Key Config", "Manage Sources", "Activity Analytics", "User Feedback"])

    with tab1:
        st.subheader("Google Fact Check API Key Config")
        current_key = st.session_state.admin_api_key or get_api_key() or ""
        new_key = st.text_input("Update API Key (Session Only)", value=current_key, type="password")
        if st.button("Set API Key"):
            st.session_state.admin_api_key = new_key
            st.success("API Key updated for the session.")
            st.rerun()

    with tab2:
        st.subheader("Manage Trusted Sources")
        sources = load_sources()
        st.write("Current Trusted Sources:")
        for s in sources:
            st.markdown(f"- `{s}`")

        col1, col2 = st.columns(2)
        with col1:
            new_source = st.text_input("Add Source")
            if st.button("Add"):
                if add_source(new_source):
                    st.success(f"Added {new_source}")
                    st.rerun()
                else:
                    st.error("Invalid or duplicate source.")
        with col2:
            rm_source = st.text_input("Remove Source")
            if st.button("Remove"):
                if remove_source(rm_source):
                    st.success(f"Removed {rm_source}")
                    st.rerun()
                else:
                    st.error("Source not found.")

    with tab3:
        st.header("Admin Dashboard")
        st.markdown("<br>", unsafe_allow_html=True)
        
        stats = get_analytics()
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Articles Analyzed", stats["total"])
        col2.metric("Number of REAL", stats["real"])
        col3.metric("Number of FAKE", stats["fake"])

        st.markdown("<br>", unsafe_allow_html=True)

        logs = get_logs()
        if logs:
            df = pd.DataFrame(logs)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                pie_data = pd.DataFrame({
                    "Prediction": ["REAL", "FAKE", "UNKNOWN"],
                    "Count": [stats["real"], stats["fake"], stats["unknown"]]
                })
                pie_data = pie_data[pie_data["Count"] > 0]
                
                if not pie_data.empty:
                    fig_pie = px.pie(
                        pie_data, 
                        names="Prediction", 
                        values="Count", 
                        title="Prediction Distribution"
                    )
                    fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                    st.plotly_chart(fig_pie, use_container_width=True)
            
            with col_chart2:
                trusted_sources = [s.lower() for s in load_sources()]
                def classify_source(s):
                    if not isinstance(s, str):
                        return "Untrusted"
                    s_lower = s.lower().strip()
                    if not s_lower or s_lower == "unknown":
                        return "Untrusted"
                    return "Trusted" if s_lower in trusted_sources else "Untrusted"
                
                if "source" in df.columns:
                    df["Source_Trust"] = df["source"].apply(classify_source)
                else:
                    df["Source_Trust"] = "Untrusted"
                    
                source_counts = df["Source_Trust"].value_counts().reset_index()
                source_counts.columns = ["Source Credibility", "Count"]
                
                fig_bar = px.bar(
                    source_counts, 
                    x="Source Credibility", 
                    y="Count", 
                    title="Source Credibility Distribution",
                    color="Source Credibility"
                )
                fig_bar.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_bar, use_container_width=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            if "timestamp" in df.columns:
                df["timestamp_dt"] = pd.to_datetime(df["timestamp"], errors="coerce")
                df["Date"] = df["timestamp_dt"].dt.date
                trend_data = df.groupby("Date").size().reset_index(name="Analyses")
                
                fig_line = px.line(
                    trend_data, 
                    x="Date", 
                    y="Analyses", 
                    title="Usage Trend Over Time", 
                    markers=True
                )
                fig_line.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_line, use_container_width=True)
            
            st.markdown("<br><hr>", unsafe_allow_html=True)
            st.subheader("Recent Logs")
            
            df_display = pd.DataFrame(reversed(logs))
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("No activity logged yet.")

    with tab4:
        st.header("User Feedback Analytics")
        st.markdown("<br>", unsafe_allow_html=True)
        
        feedbacks = load_feedback()
        if not feedbacks:
            st.info("No user feedback collected yet.")
        else:
            total_feedback = len(feedbacks)
            pos_count = sum(1 for f in feedbacks if f.get("sentiment") == "Positive")
            neg_count = sum(1 for f in feedbacks if f.get("sentiment") == "Negative")
            neu_count = sum(1 for f in feedbacks if f.get("sentiment") == "Neutral")
            
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.metric("Total Feedback Count", total_feedback)
            col_f2.metric("Positive Reviews", pos_count)
            col_f3.metric("Negative Reviews", neg_count)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            pie_data_f = pd.DataFrame({
                "Sentiment": ["Positive", "Negative", "Neutral"],
                "Count": [pos_count, neg_count, neu_count]
            })
            pie_data_f = pie_data_f[pie_data_f["Count"] > 0]
            
            if not pie_data_f.empty:
                fig_pie_f = px.pie(
                    pie_data_f, 
                    names="Sentiment", 
                    values="Count", 
                    title="Sentiment Distribution",
                    color="Sentiment",
                    color_discrete_map={"Positive": "#16A34A", "Negative": "#DC2626", "Neutral": "#6b7280"}
                )
                fig_pie_f.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_pie_f, use_container_width=True)
            
            if neg_count > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("Actionable Insights")
                with st.expander("View Negative Feedback"):
                    for f in feedbacks:
                        if f.get("sentiment") == "Negative":
                            st.write(f"**Timestamp:** {f.get('timestamp')}")
                            st.write(f"**Predicted:** {f.get('prediction')} | **Actual:** {f.get('actual')}")
                            st.write(f"**Feedback:** {f.get('feedback')}")
                            st.markdown("---")


def render_user_mode():
    inject_custom_css()

    st.markdown('<div class="title-h1">Fake News Detection &amp; Verification Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Analyze news credibility using AI and fact-checking</div>', unsafe_allow_html=True)

    with st.container():
        article_text = st.text_area(
            "Article Text",
            height=200,
            placeholder="Paste the full news article text here..."
        )
        source_name = st.text_input(
            "Source Name",
            placeholder="Optional: e.g. BBC, Reuters, CNN"
        )
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    analyze_clicked = st.button("Analyze")

    if analyze_clicked:
        st.session_state.has_results = False
        st.session_state.show_feedback_form = False

    if not analyze_clicked and not st.session_state.get("has_results", False):
        st.markdown("""
            <div class="custom-footer">
                Built using NLP &bull; Transformers &bull; Fact Check API
            </div>
        """, unsafe_allow_html=True)
        return

    if analyze_clicked:
        if not article_text.strip():
            st.error("Please provide article text before clicking Analyze.")
            return

        with st.spinner("Analyzing..."):
            try:
                cleaned_text = clean_text(article_text)
                if not cleaned_text:
                    st.error("The text could not be processed. Please try again.")
                    return

                claims = extract_claims(cleaned_text)
                prediction = classify_text(cleaned_text)
                label = prediction.get("label", "ERROR")
                confidence = prediction.get("confidence", 0.0)

                if label == "ERROR":
                    st.error("An error occurred during classification. Please try again.")
                    return

                explanation = explain_prediction(cleaned_text, prediction, claims)
                source_trust = check_source_trust(source_name)
                fact_check_results = fact_check_claims(claims)

                log_analysis(
                    label=label,
                    confidence=confidence,
                    source_name=source_name,
                    char_length=len(cleaned_text)
                )
                
                st.session_state.results = {
                    "label": label,
                    "confidence": confidence,
                    "explanation": explanation,
                    "source_trust": source_trust,
                    "claims": claims,
                    "fact_check_results": fact_check_results,
                    "cleaned_text": cleaned_text
                }
                st.session_state.has_results = True

            except Exception:
                logger.exception("Unexpected error during analysis.")
                st.error("An unexpected error occurred. Please try again.")
                return

    # Extract valid state results for display
    res = st.session_state.results
    label = res.get("label", "UNKNOWN")
    confidence = res.get("confidence", 0.0)
    explanation = res.get("explanation", [])
    source_trust = res.get("source_trust", "Unknown")
    claims = res.get("claims", [])
    fact_check_results = res.get("fact_check_results", [])
    cleaned_text = res.get("cleaned_text", "")

    st.markdown("---")
    
    # ── 1. PREDICTION BOX ────────────────────────────────────────────────────
    if label == "REAL":
        box_class = "box-prediction-real"
    elif label == "FAKE":
        box_class = "box-prediction-fake"
    else:
        box_class = "box-prediction-uncertain"
    
    pred_html = f"""
        <div class="card">
            <div class="box-label">Prediction Results</div>
            <div class="{box_class}">
                <b>Prediction:</b> {label}<br>
                <b>Confidence:</b> {format_confidence(confidence)}
            </div>
        </div>
    """
    st.markdown(pred_html, unsafe_allow_html=True)
    
    # ── 2. SOURCE CREDIBILITY BOX ────────────────────────────────────────────
    source_display = source_name.strip() if source_name.strip() else "Unknown"
    if "Trusted" in source_trust or source_trust == "Trusted":
        source_class = "box-source-trusted"
    else:
        source_class = "box-source-untrusted"
        
    src_html = f"""
        <div class="card">
            <div class="box-label">Source Credibility</div>
            <div class="{source_class}">
                <b>Source:</b> {source_display}<br>
                <b>Status:</b> {source_trust}
            </div>
        </div>
    """
    st.markdown(src_html, unsafe_allow_html=True)

    # ── 3. EXTRACTED CLAIMS BOX ──────────────────────────────────────────────
    if claims:
        claims_items = "".join(f"<li style='margin-bottom:0.4rem;'>{c}</li>" for c in claims[:3])
        claims_html = f"""
            <div class="card">
                <div class="box-label">Extracted Claims</div>
                <div class="box-claims">
                    <ul style="margin: 0; padding-left: 1.2rem;">{claims_items}</ul>
                </div>
            </div>
        """
        st.markdown(claims_html, unsafe_allow_html=True)

    # ── 4. EXPLANATION BOX ───────────────────────────────────────────────────
    if explanation:
        explanation_text = " ".join(explanation[:3])
        exp_html = f"""
            <div class="card">
                <div class="box-label">AI Explanation</div>
                <div class="box-explanation">
                    {explanation_text}
                </div>
            </div>
        """
        st.markdown(exp_html, unsafe_allow_html=True)

    # ── 5. FACT CHECK RESULTS ────────────────────────────────────────────────
    valid_checks = [
        res for res in (fact_check_results or [])
        if res.get("verdict") and res.get("verdict") != "No verified fact-check found"
    ]
    if valid_checks:
        fc_html = '<div class="card"><div class="box-label">Fact Check Results</div>'
        for res in valid_checks:
            link_html = (
                f'<br><a href="{res.get("link")}" target="_blank" '
                f'style="color:#2563EB; font-size:0.9rem; text-decoration: none;">&rarr; Read more</a>'
                if res.get("link") else ""
            )
            fc_html += f"""
                <div class="box-factcheck">
                    <b>Claim:</b> {res['claim']}<br>
                    <b>Verdict:</b> <span style="color:#DC2626; font-weight:600;">{res.get('verdict')}</span><br>
                    <b>Publisher:</b> {res.get('publisher')}
                    {link_html}
                </div>
            """
        fc_html += '</div>'
        st.markdown(fc_html, unsafe_allow_html=True)

    # ── 6. USER FEEDBACK ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if not st.session_state.get("show_feedback_form"):
        if st.button("Give Feedback"):
            st.session_state.show_feedback_form = True
            st.rerun()

    if st.session_state.get("show_feedback_form", False):
        with st.form("feedback_form"):
            st.subheader("We value your feedback!")
            feedback_type = st.radio("Feedback Type", ["Prediction Correct", "Prediction Wrong"], horizontal=True)
            actual_truth = st.radio("Actual Truth", ["Real News", "Fake News"], horizontal=True)
            user_experience = st.text_area("User Experience", placeholder="Explain why you think the result is incorrect or correct")
            rating = st.slider("Rating", 1, 5, 3)
            
            submitted_feedback = st.form_submit_button("Submit Feedback")
            if submitted_feedback:
                actual_val = "REAL" if actual_truth == "Real News" else "FAKE"
                save_feedback(cleaned_text, label, actual_val, user_experience, rating)
                st.success("Thank you for your feedback!")
                st.session_state.show_feedback_form = False

    # ── FOOTER ───────────────────────────────────────────────────────────────
    st.markdown("""
        <div class="custom-footer">
            Built using NLP &bull; Transformers &bull; Fact Check API
        </div>
    """, unsafe_allow_html=True)


def main():
    logger.info("App started.")
    init_session_state()

    st.sidebar.title("Navigation")
    mode = st.sidebar.radio("Mode", ["User Mode", "Admin Dashboard"])

    if mode == "User Mode":
        render_user_mode()
    else:
        render_admin_dashboard()

if __name__ == "__main__":
    main()
