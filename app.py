import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Streamlit Fallback Detection
# If this file is run via `streamlit run app.py`
is_streamlit = "streamlit" in sys.argv[0]

if is_streamlit:
    import streamlit as st
    from services.preprocess import clean_text
    from services.predictor import predict_news
    from services.claim_extractor import extract_claims
    from services.explainability import explain_claims
    from services.factcheck_api import verify_claim
    
    st.set_page_config(page_title="Fake News Detection MVP", layout="wide")
    st.title("Fake News Detection & Verification")
    
    text = st.text_area("Enter Article Text:")
    if st.button("Analyze"):
        if not text.strip():
            st.error("Please enter text.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    cleaned = clean_text(text)
                    prediction = predict_news(cleaned)
                    claims = extract_claims(cleaned)
                    explained = explain_claims(claims)
                    fact_checks = [verify_claim(c) for c in claims]
                    
                    st.subheader("Prediction")
                    color = "red" if prediction["label"] == "FAKE" else "green"
                    st.markdown(f"**Verdict:** <span style='color:{color}'>{prediction['label']}</span> (Confidence: {prediction['confidence']:.2f})", unsafe_allow_html=True)
                    
                    st.subheader("Extracted Claims & Explainability")
                    for e, f in zip(explained, fact_checks):
                        with st.expander(e["claim"]):
                            st.write(f"**Suspicious Score:** {e['suspicious_score']}")
                            st.write(f"**Suspicious Words:** {', '.join(e['suspicious_words']) if e['suspicious_words'] else 'None'}")
                            st.write(f"**Fact Check Verdict:** {f['verdict']} (from {f['publisher']})")
                            if f['url']:
                                st.write(f"**Source URL:** {f['url']}")
                except Exception as e:
                    st.error(f"Error during analysis: {e}")

else:
    # Flask Primary Application
    from flask import Flask, request, jsonify, render_template
    from services.preprocess import clean_text
    from services.predictor import predict_news
    from services.claim_extractor import extract_claims
    from services.explainability import explain_claims
    from services.factcheck_api import verify_claim
    from services.source_manager import get_sources, add_source, remove_source

    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/analyze', methods=['POST'])
    def analyze():
        try:
            data = request.get_json()
            if not data or 'text' not in data:
                return jsonify({"error": "Please enter text."}), 400
            
            raw_text = data['text']
            if not raw_text.strip():
                return jsonify({"error": "Please enter text."}), 400

            cleaned = clean_text(raw_text)
            prediction = predict_news(cleaned)
            claims = extract_claims(cleaned)
            explained = explain_claims(claims)
            
            fact_checks = []
            for claim in claims:
                fc = verify_claim(claim)
                fact_checks.append(fc)

            return jsonify({
                "prediction": prediction,
                "claims": claims,
                "explainability": explained,
                "fact_checks": fact_checks
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/sources', methods=['GET', 'POST', 'DELETE'])
    def sources():
        try:
            if request.method == 'GET':
                return jsonify({"sources": get_sources()})
            elif request.method == 'POST':
                data = request.get_json()
                if not data or 'source' not in data:
                    return jsonify({"error": "Invalid payload"}), 400
                add_source(data['source'])
                return jsonify({"success": True, "message": "Added source."})
            elif request.method == 'DELETE':
                data = request.get_json()
                if not data or 'source' not in data:
                    return jsonify({"error": "Invalid payload"}), 400
                remove_source(data['source'])
                return jsonify({"success": True, "message": "Removed source."})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/metrics', methods=['GET'])
    def metrics():
        return jsonify({
            "articles": 123,
            "accuracy": 0.92,
            "uptime": "99.9%",
            "users": 45
        })

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)
