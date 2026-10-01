import time
import httpx
import streamlit as st

st.set_page_config(page_title="Eocean AI Assistant", page_icon="", layout="centered")

# ---------- Styling ----------
st.markdown(
    """
    <style>
      .block-container {max-width: 820px; padding-top: 2rem;}
      .hero {
        background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        border-radius: 18px; padding: 26px 30px; color: white; margin-bottom: 1.2rem;
      }
      .hero h1 {margin: 0; font-size: 1.9rem; color: white;}
      .hero p {margin: 6px 0 0; opacity: .9;}
      .chip {
        display: inline-block; padding: 2px 10px; margin: 2px 4px 0 0;
        border-radius: 999px; font-size: .75rem;
        background: rgba(99,102,241,.15); color: #6366f1; border: 1px solid rgba(99,102,241,.35);
      }
      .meta {font-size: .75rem; opacity: .65; margin-top: 6px;}
      div[data-testid="stSidebar"] .stButton button {
        text-align: left; width: 100%; border-radius: 10px;
      }
    </style>
    <div class="hero">
      <h1>Eocean AI Assistant</h1>
      <p>Ask anything about Eocean's services, products, APIs and company profile.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
SAMPLES = [
    "What services does Eocean offer?",
    "Which customers use the WhatsApp Business API and for what?",
    "Compare SMS, WhatsApp, Voice and RCS",
    "Summarise Eocean's timeline from 2008 to 2026",
    "List all Voice OTP request parameters",
    "What are the partner programmes and their pricing?",
    "Who are Eocean's competitors?",
    "Who is Eocean's CFO?",
]

with st.sidebar:
    st.header("⚙️ Settings")
    api_url = st.text_input("API URL", "http://127.0.0.1:8000/query/")
    show_meta = st.toggle("Show sources & timing", value=True)

    st.divider()
    st.subheader("💡 Try these")
    for q in SAMPLES:
        if st.button(q, key=f"sample_{q}"):
            st.session_state.pending = q

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------- State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []


def render_meta(m: dict):
    if not show_meta or "sources" not in m:
        return
    chips = "".join(f'<span class="chip">Page {p}</span>' for p in m["sources"])
    st.markdown(
        f"{chips}<div class='meta'>⏱ {m['client_s']}s total · server {m.get('total_s', '?')}s · "
        f"attempts: {m.get('attempts', 1)}</div>",
        unsafe_allow_html=True,
    )


# ---------- History ----------
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "🌊"):
        st.markdown(m["content"])
        if m["role"] == "assistant":
            render_meta(m)

# ---------- Input ----------
prompt = st.chat_input("Ask about Eocean...") or st.session_state.pop("pending", None)

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🌊"):
        with st.spinner("Searching the knowledge base..."):
            t = time.perf_counter()
            try:
                r = httpx.post(api_url, json={"query": prompt}, timeout=120)
                r.raise_for_status()
                data = r.json()
                reply = {
                    "role": "assistant",
                    "content": data.get("answer", "No answer returned."),
                    "sources": data.get("sources", []),
                    "attempts": data.get("attempts", 1),
                    "total_s": data.get("total_s"),
                    "client_s": round(time.perf_counter() - t, 2),
                }
            except httpx.ConnectError:
                reply = {"role": "assistant", "content": "❌ Can't reach the API. Is `uvicorn main:app --reload` running?"}
            except httpx.HTTPStatusError as e:
                reply = {"role": "assistant", "content": f"❌ API error {e.response.status_code}. Check the uvicorn terminal."}
            except Exception as e:
                reply = {"role": "assistant", "content": f"❌ Unexpected error: {e}"}

        st.markdown(reply["content"])
        render_meta(reply)

    st.session_state.messages.append(reply)