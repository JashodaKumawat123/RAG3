import os, json, time, io, uuid
import streamlit as st
import pandas as pd
from PIL import Image
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    print("OpenCV not available - video processing will be disabled")
from core.rag import RAGEngine, format_context
from core.path import personalize_path
from core.user import upsert_user, get_user, log_progress, get_progress, log_interaction
from core.mm import CLIPIndexer
from core.competency import topological_sequence, get_prerequisites, get_objectives
from core.analytics import estimate_mastery, predict_performance, identify_gaps, recommend_remediation, choose_difficulty
from core.quizzes import load_quiz_packs, grade_quiz

st.set_page_config(page_title="EduRAG: Learning Path RAG", layout="wide")
st.title("🎓 EduRAG — Personalized Learning Path RAG (DSA + Multimodal)")

# Sidebar: user + settings
with st.sidebar:
    st.header("User & Settings")
    user_id = st.text_input("User ID", value="student_001")
    level = st.selectbox("Student Level", ["beginner","intermediate","advanced"], index=0)
    style = st.selectbox("Learning Style", ["visual","auditory","read/write","kinesthetic"], index=0)
    goals = st.multiselect("Target Competencies", ["arrays","linked-lists","stacks","queues","trees","graphs","dp"], default=["arrays","linked-lists","trees"])
    if st.button("Save Profile"):
        upsert_user(user_id, {"level":level, "style":style, "goals":goals})
        st.success("Profile saved.")

st.markdown("---")
tabs = st.tabs(["📥 Ingest","🛤️ Learning Path","💬 Ask (RAG)","🖼️ Cross‑modal Search","📝 Quiz","📈 Progress","🧪 Evaluate"])

# Lazy init engines
if "rag" not in st.session_state:
    st.session_state.rag = RAGEngine()
if "clip" not in st.session_state:
    st.session_state.clip = CLIPIndexer()

# Tab 1: Ingest
with tabs[0]:
    st.subheader("Content Ingestion")
    st.caption("Upload CSV (like sample_resources.csv) for text/PDF/links, and optionally upload images/videos/audio+transcripts for multimodal.")
    csv = st.file_uploader("CSV of resources", type=["csv"])
    if st.button("Ingest CSV"):
        if csv:
            tmp = f"tmp_{int(time.time())}.csv"
            with open(tmp, "wb") as f:
                f.write(csv.read())
            n = st.session_state.rag.ingest_csv(tmp)
            os.remove(tmp)
            st.success(f"Ingested {n} text chunks into Chroma.")
            st.info("Content is categorized by 'competencies' metadata for sequencing and remediation.")
        else:
            st.warning("Upload a CSV first.")

    st.write("— **Multimodal Uploads** —")
    imgs = st.file_uploader("Images (PNG/JPG)", type=["png","jpg","jpeg"], accept_multiple_files=True)
    vids = st.file_uploader("Videos (MP4/MOV/AVI)", type=["mp4","mov","avi"], accept_multiple_files=True)
    auds = st.file_uploader("Audio (MP3/WAV) + transcript (optional .txt)", type=["mp3","wav","txt"], accept_multiple_files=True)
    comp = st.multiselect("Competencies for media", ["arrays","linked-lists","stacks","queues","trees","graphs","dp"], default=["arrays"])
    if st.button("Ingest Media"):
        added = 0
        # Images
        if imgs:
            items = []
            for f in imgs:
                try:
                    pil = Image.open(io.BytesIO(f.read())).convert("RGB")
                    items.append({"id": f"img-{uuid.uuid4().hex}", "pil": pil, "meta": {"type":"image","filename":f.name,"competencies":",".join(comp)}})
                except Exception as e:
                    st.error(f"Image {f.name} error: {e}")
            added += st.session_state.clip.add_images(items)
        # Videos (extract frames every N seconds)
        if vids and OPENCV_AVAILABLE:
            for f in vids:
                tmp = f"tmp_{uuid.uuid4().hex}_{f.name}"
                with open(tmp, "wb") as out:
                    out.write(f.read())
                cap = cv2.VideoCapture(tmp)
                fps = cap.get(cv2.CAP_PROP_FPS) or 24
                step = int(fps*3)  # every ~3 seconds
                idx = 0
                items = []
                while True:
                    ret, frame = cap.read()
                    if not ret: break
                    if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % step == 0:
                        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        pil = Image.fromarray(rgb)
                        items.append({"id": f"vid-{os.path.basename(tmp)}-f{idx}-{uuid.uuid4().hex}", "pil": pil,
                                      "meta": {"type":"video-frame","video":f.name,"frame_idx":idx,"competencies":",".join(comp)}})
                        idx += 1
                        if idx >= 20:  # limit per video
                            break
                cap.release()
                os.remove(tmp)
                if items:
                    added += st.session_state.clip.add_images(items)
        elif vids and not OPENCV_AVAILABLE:
            st.warning("Video processing is disabled in this environment. Only images and audio transcripts will be processed.")
        # Audio (store transcript as text into primary RAG)
        if auds:
            for f in auds:
                if f.name.lower().endswith(".txt"):
                    text = f.read().decode("utf-8", errors="ignore")
                    rows = [{
                        "id": f"aud-trans-{uuid.uuid4().hex}",
                        "title": f"Audio Transcript: {f.name}",
                        "type": "text",
                        "url": "",
                        "content": text,
                        "competencies": ",".join(comp),
                        "level": level
                    }]
                    df = pd.DataFrame(rows)
                    tmpcsv = f"tmp_{uuid.uuid4().hex}.csv"
                    df.to_csv(tmpcsv, index=False)
                    st.session_state.rag.ingest_csv(tmpcsv)
                    os.remove(tmpcsv)
            st.info("Audio transcripts ingested into text RAG. For speech-to-text, connect Whisper or a hosted ASR in backend.")
        st.success(f"Media indexed: {added} (images/frames).")

# Tab 2: Learning Path
with tabs[1]:
    st.subheader("Personalized Learning Path")
    seq = topological_sequence(goals)
    mastery = estimate_mastery(user_id)
    rows = []
    for c in seq:
        prereqs = ", ".join(get_prerequisites(c))
        objectives = "; ".join(get_objectives(c))
        rec_diff = choose_difficulty(level, mastery.get(c, 0.5))
        rows.append({
            "competency": c,
            "prerequisites": prereqs,
            "objectives": objectives,
            "recommended_difficulty": rec_diff
        })
    st.dataframe(pd.DataFrame(rows))
    st.caption("Sequenced by prerequisites; objectives listed per competency. Difficulty adapts to your mastery.")

# Tab 3: Ask (RAG)
with tabs[2]:
    st.subheader("Grounded Q&A")
    q = st.text_input("Ask a question about DSA or your resources")
    k = st.slider("Top-k", 1, 10, 5)
    if st.button("Search & Answer"):
        hits = st.session_state.rag.query(q, k=k)
        st.write("### Retrieved context")
        for h in hits:
            st.markdown(f"**{h['meta'].get('title','')}** — {h['meta'].get('competencies','')}  \n`dist={h['dist']:.3f}`")
            st.code(h["doc"][:500])
        ctx = format_context(hits)
        st.markdown("### Draft Answer (LLM placeholder)")
        st.write("Connect your preferred LLM in backend. For now, here's a context-aware template:")
        st.code(f"Question: {q}\n\nAnswer (based on retrieved context):\n{ctx[:800]}...")

# Tab 4: Cross-modal Search
with tabs[3]:
    st.subheader("Text → Image/Video frame search (CLIP)")
    q2 = st.text_input("Describe what you want to see (e.g., 'binary tree traversal diagram')")
    k2 = st.slider("Top-k images", 1, 20, 8)
    if st.button("Search Media"):
        results = st.session_state.clip.query(q2, k=k2, where={})
        cols = st.columns(4)
        shown = 0
        for r in results:
            meta = r["meta"]
            with cols[shown % 4]:
                st.caption(f"{meta.get('type')} | {meta.get('competencies','')} | d={r['dist']:.3f}")
                st.json(meta)
            shown += 1
        if shown == 0:
            st.info("No media found yet. Ingest some images or videos above.")

# Tab 5: Quiz
with tabs[4]:
    st.subheader("Quiz")
    packs = load_quiz_packs()
    if not packs:
        st.info("No quiz packs found in content/quizzes. A sample has been added; refresh if needed.")
    titles = [f"{p.get('title','Untitled')} ({p.get('competency','')})" for p in packs]
    sel = st.selectbox("Choose a quiz", titles if titles else ["No quizzes available"])
    if packs:
        idx = titles.index(sel)
        pack = packs[idx]
        st.caption(f"Competency: {pack.get('competency','')} | Level: {pack.get('level','')}")
        user_answers = []
        for i, q in enumerate(pack.get("questions", [])):
            st.markdown(f"**Q{i+1}. {q.get('question','')}**")
            choice = st.radio(" ", q.get("options", []), key=f"q_{i}", index=None, horizontal=False)
            try:
                user_answers.append(q.get("options", []).index(choice) if choice is not None else -1)
            except ValueError:
                user_answers.append(-1)
        if st.button("Submit Quiz"):
            result = grade_quiz(pack, user_answers)
            st.success(f"Score: {result['correct']}/{result['total']} ({result['score']*100:.0f}%)")
            # Log as interaction for mastery analytics
            comp = pack.get("competency", "")
            # Map textual level to numeric difficulty
            lvl = str(pack.get("level", "beginner")).lower()
            diff = 0.33 if lvl == "beginner" else (0.66 if lvl == "intermediate" else 0.9)
            log_interaction(user_id, comp, float(result['score']), float(diff), 0.0)
            # Quick remediation for this competency
            st.write("### Recommended Remediation")
            recs = recommend_remediation(user_id, [comp], st.session_state.rag, st.session_state.clip, style, k_text=3, k_media=4)
            bundle = recs.get(comp, {})
            st.write("Text:")
            for h in bundle.get("text", [])[:3]:
                st.markdown(f"- **{h['meta'].get('title','')}** — {h['meta'].get('competencies','')}")
            st.write("Media:")
            for r in bundle.get("media", [])[:4]:
                st.json(r.get("meta", {}))

# Tab 6: Progress
with tabs[5]:
    st.subheader("Progress Tracking & Adaptation")
    topic = st.selectbox("Topic", ["arrays","linked-lists","stacks","queues","trees","graphs","dp"])
    status = st.selectbox("Status", ["started","in-progress","completed"])
    score = st.slider("Mastery Score", 0.0, 1.0, 0.7, 0.05)
    if st.button("Log Progress"):
        log_progress(user_id, topic, status, float(score))
        st.success("Logged!")
    st.write("### History")
    st.dataframe(pd.DataFrame(get_progress(user_id)))

    st.write("### Mastery Estimation")
    m = estimate_mastery(user_id)
    st.bar_chart(pd.Series(m))

    st.write("### Predicted Performance")
    cols = st.columns(3)
    for i, c in enumerate(["arrays","linked-lists","trees"]):
        with cols[i % 3]:
            p = predict_performance(user_id, c, difficulty=0.5)
            st.metric(label=f"{c} success prob", value=f"{p:.2f}")

    st.write("### Knowledge Gaps")
    gaps = identify_gaps(user_id)
    if gaps:
        st.warning(", ".join(gaps))
    else:
        st.success("No gaps detected under current threshold.")

    if st.button("Recommend Remediation"):
        recs = recommend_remediation(user_id, goals, st.session_state.rag, st.session_state.clip, style)
        for comp, bundle in recs.items():
            st.markdown(f"#### {comp}")
            st.write("Text resources:")
            for h in bundle.get("text", [])[:3]:
                st.markdown(f"- **{h['meta'].get('title','')}** — {h['meta'].get('competencies','')}")
            st.write("Media results:")
            for r in bundle.get("media", [])[:4]:
                st.json(r.get("meta", {}))

# Tab 7: Evaluate (basic retrieval metrics placeholder)
with tabs[6]:
    st.subheader("Evaluation")
    st.write("Add your labeled Q→gold doc ids to compute precision@k / MRR. RAGAS can be integrated similarly.")
    st.info("This starter focuses on scaffolding. Extend with real metrics in core/eval.py.")
