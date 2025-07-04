import ollama
import streamlit as st
import markdown2

# Initialize session state for conversation history, user info, and to-do list
if "messages" not in st.session_state:
    st.session_state.messages = []
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "todo_list" not in st.session_state:
    st.session_state.todo_list = []

# Get response from local LLM
def get_llm_response(prompt, model='gemma3:1b'):
    try:
        response = ollama.chat(model=model, messages=[
            {"role": "system", "content": "You are Bali.AI, a friendly and helpful personal assistant. Provide concise, accurate, and user-friendly responses in Markdown format."},
            {"role": "user", "content": prompt}
        ])
        return response['message']['content'].strip()
    except Exception as e:
        return f"⚠️ Error: Could not connect to the model. Please check if {model} is running locally. ({str(e)})"

# Add task to to-do list
def add_todo(task):
    if task and task not in st.session_state.todo_list:
        st.session_state.todo_list.append(task)
        return f"✅ Added to your to-do list: {task}"
    return "⚠️ Task is empty or already exists."

# Streamlit UI
def main():
    st.set_page_config(page_title="Bali.AI", page_icon="🤖")
    st.title("🤖 Bali.AI - Your Personal Assistant")
    
    # User name input for personalization
    if not st.session_state.user_name:
        with st.form(key="name_form"):
            st.markdown("Welcome! Let's get to know each other.")
            user_name = st.text_input("What's your name?")
            name_submit = st.form_submit_button("Save")
            if name_submit and user_name:
                st.session_state.user_name = user_name
                st.success(f"Hi, {user_name}! I'm ready to assist you.")
                st.rerun()

    else:
        st.markdown(f"Welcome back, **{st.session_state.user_name}**! How can I assist you today?")

        # Sidebar for to-do list
        with st.sidebar:
            st.subheader("📋 Your To-Do List")
            if st.session_state.todo_list:
                for i, task in enumerate(st.session_state.todo_list):
                    st.write(f"- {task}")
                    if st.button(f"Remove", key=f"remove_{i}"):
                        st.session_state.todo_list.pop(i)
                        st.rerun()
            else:
                st.write("No tasks yet!")
            
            todo_input = st.text_input("Add a task")
            if st.button("Add Task"):
                result = add_todo(todo_input)
                st.write(result)

        # Display conversation history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Input form
        with st.form(key="query_form"):
            col1, col2 = st.columns([3, 1])
            with col1:
                question = st.text_input("💬 Ask me anything", key="user_input")
            with col2:
                action = st.selectbox("Action", ["Ask", "Summarize", "Translate to Spanish"], key="action")
            submit_button = st.form_submit_button("Submit")

        if submit_button and question:
            with st.spinner("🧠 Thinking..."):
                # Add user message to history
                st.session_state.messages.append({"role": "user", "content": question})
                with st.chat_message("user"):
                    st.markdown(question)

                # Generate response based on selected action
                prompt = question
                if action == "Summarize":
                    prompt = f"Summarize this text: {question}"
                elif action == "Translate to Spanish":
                    prompt = f"Translate this to Spanish: {question}"
                
                response = get_llm_response(prompt)
                formatted_response = markdown2.markdown(response)  # Render Markdown

                # Add assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.markdown(formatted_response)
                
                st.balloons()

        # Clear conversation history
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()