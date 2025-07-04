import ollama
import streamlit as st
import json
import os
from datetime import datetime
import streamlit.components.v1 as components

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "todo_list" not in st.session_state:
    st.session_state.todo_list = []
if "reminders" not in st.session_state:
    st.session_state.reminders = []
if "preferences" not in st.session_state:
    st.session_state.preferences = {"tone": "Friendly"}

# File to store tasks/reminders
DATA_FILE = "bali_ai_data.json"

# Load/save data to JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            st.session_state.todo_list = data.get("todo_list", [])
            st.session_state.reminders = data.get("reminders", [])

def save_data():
    data = {
        "todo_list": st.session_state.todo_list,
        "reminders": st.session_state.reminders
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# Get LLM response with context
def get_llm_response(prompt, model='gemma3:1b'):
    try:
        messages = [{"role": "system", "content": f"You are Bali.AI, a personal assistant for {st.session_state.user_name or 'User'}. Use a {st.session_state.preferences['tone']} tone and respond in English. Provide concise, accurate responses in simple Markdown format (e.g., use **bold**, *italic*, - lists). Answer as a helpful assistant."}]
        messages.extend(st.session_state.messages[-5:])
        messages.append({"role": "user", "content": prompt})
        response = ollama.chat(model=model, messages=messages)
        return response['message']['content'].strip()
    except Exception as e:
        try:
            response = ollama.chat(model='gemma2:2b', messages=messages)
            return response['message']['content'].strip()
        except:
            return f"⚠️ Error: Could not connect to any model. Please check if Ollama is running. ({str(e)})"

# Add task to to-do list
def add_todo(task):
    if task and task not in st.session_state.todo_list:
        st.session_state.todo_list.append(task)
        save_data()
        return f"✅ Added to your to-do list: {task}"
    return "⚠️ Task is empty or already exists."

# Add reminder
def add_reminder(task, time):
    reminder = {"task": task, "time": time, "created": datetime.now().isoformat()}
    st.session_state.reminders.append(reminder)
    save_data()
    return f"⏰ Reminder set: {task} at {time}"

# Get time-based greeting
def get_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Capabilities in simple Markdown
CAPABILITIES = """
### Bali.AI Capabilities
- **Conversational Chat**: Have natural, friendly conversations, remembering up to 5 previous messages.
- **Summarization**: Condense long texts into short summaries, great for articles or notes.
- **Task Management**: Add, view, and remove tasks in a to-do list, saved locally.
- **Reminders**: Set time-based reminders for events or tasks, stored persistently.
- **Personalization**: Customize responses with your name and tone (Friendly, Formal, Casual).
- **Local Processing**: Runs on your device with `gemma3:1b` or `gemma2:2b`, ensuring privacy.

### Limitations
- **No Real-Time Web Access**: Responses use model data (up to March 2025), no live internet.
- **Resource Constraints**: Limited by ~4GB RAM; complex tasks may be slow.
- **Text-Only**: Cannot process images, audio, or other non-text inputs.
- **No Professional Advice**: Not qualified for medical, legal, or financial advice. Consult professionals.
- **Emotional Understanding**: Can interpret emotional language but lacks true empathy.
- **Model Dependency**: Requires Ollama and `gemma3:1b` or `gemma2:2b`.
"""

# JavaScript for auto-scrolling
SCROLL_SCRIPT = """
<script>
    const chatContainer = window.parent.document.querySelector('.chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
</script>
"""

# Streamlit UI
def main():
    st.set_page_config(page_title="Bali.AI", page_icon="🤖")
    st.title("🤖 Bali.AI - Your Personal Assistant")
    
    # Load saved data
    load_data()

    # User name input
    if not st.session_state.user_name:
        with st.form(key="name_form"):
            st.markdown("Welcome! Let's get to know each other.")
            user_name = st.text_input("What's your name?")
            name_submit = st.form_submit_button("Save")
            if name_submit and user_name:
                st.session_state.user_name = user_name
                st.success(f"{get_greeting()}, {user_name}! I'm ready to assist you.")
                st.rerun()
    else:
        st.markdown(f"{get_greeting()}, **{st.session_state.user_name}**! How can I assist you today?")

        # Sidebar for settings, capabilities, and to-do list
        with st.sidebar:
            st.subheader("ℹ️ About Bali.AI")
            with st.expander("Capabilities & Limitations"):
                st.markdown(CAPABILITIES, unsafe_allow_html=True)

            st.subheader("⚙️ Settings")
            st.session_state.preferences["tone"] = st.selectbox("Tone", ["Friendly", "Formal", "Casual"], index=["Friendly", "Formal", "Casual"].index(st.session_state.preferences["tone"]))
            
            st.subheader("📋 To-Do List")
            if st.session_state.todo_list:
                for i, task in enumerate(st.session_state.todo_list):
                    st.write(f"- {task}")
                    if st.button(f"Remove", key=f"remove_todo_{i}"):
                        st.session_state.todo_list.pop(i)
                        save_data()
                        st.rerun()
            else:
                st.write("No tasks yet!")
            todo_input = st.text_input("Add a task")
            if st.button("Add Task"):
                result = add_todo(todo_input)
                st.write(result)

            st.subheader("⏰ Reminders")
            if st.session_state.reminders:
                for i, reminder in enumerate(st.session_state.reminders):
                    st.write(f"- {reminder['task']} at {reminder['time']}")
                    if st.button(f"Delete", key=f"remove_reminder_{i}"):
                        st.session_state.reminders.pop(i)
                        save_data()
                        st.rerun()
            else:
                st.write("No reminders yet!")
            reminder_task = st.text_input("Reminder task")
            reminder_time = st.text_input("Time (e.g., 2025-07-04 14:00)")
            if st.button("Set Reminder"):
                result = add_reminder(reminder_task, reminder_time)
                st.write(result)

        # Chat interface
        st.markdown("### 💬 Chat")
        chat_container = st.container()
        chat_container.markdown('<div class="chat-container" style="max-height: 400px; overflow-y: auto;">', unsafe_allow_html=True)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(f"**{message['role'].capitalize()} ({message['timestamp']})**: {message['content']}", unsafe_allow_html=True)
        chat_container.markdown('</div>', unsafe_allow_html=True)

        # Input form
        with st.form(key="query_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                question = st.text_input("Ask me anything", key="user_input")
            with col2:
                action = st.selectbox("Action", ["Ask", "Summarize"], key="action")
            submit_button = st.form_submit_button("Submit")

        if submit_button and question:
            with st.spinner("🧠 Thinking..."):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({"role": "user", "content": question, "timestamp": timestamp})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(f"**User ({timestamp})**: {question}", unsafe_allow_html=True)

                # Generate response based on action
                prompt = question
                if action == "Summarize":
                    prompt = f"Summarize this text: {question}"
                elif question.lower().startswith("what can you do") or question.lower().startswith("capabilities"):
                    prompt = "Describe your capabilities and limitations in simple Markdown format (e.g., use **bold**, *italic*, - lists)."

                response = get_llm_response(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": timestamp})
                with chat_container:
                    with st.chat_message("assistant"):
                        st.markdown(f"**Assistant ({timestamp})**: {response}", unsafe_allow_html=True)
                
                # Auto-scroll to bottom
                components.html(SCROLL_SCRIPT, height=0)
                #st.balloons()

        # Clear chat history
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()