import streamlit as st
import requests
import json
from groq import Groq
import os

# Set page config
st.set_page_config(
    page_title="AI Code Explainer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .code-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #667eea;
    }
    
    .explanation-container {
        background-color: #e8f5e8;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #28a745;
    }
    
    .stTextArea textarea {
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

def initialize_groq_client():
    """Initialize Groq client with API key"""
    api_key = st.session_state.get('groq_api_key', '')
    if api_key:
        try:
            client = Groq(api_key=api_key)
            return client
        except Exception as e:
            st.error(f"Error initializing Groq client: {str(e)}")
            return None
    return None

def explain_code(client, code_snippet, programming_language, complexity_level):
    """Send code to Groq API for explanation"""
    try:
        # Customize the prompt based on complexity level
        complexity_prompts = {
            "Beginner": "Explain this code in very simple terms, as if talking to someone who just started programming. Use everyday language and avoid technical jargon.",
            "Intermediate": "Explain this code clearly, including the main concepts and how different parts work together. Use some technical terms but explain them.",
            "Advanced": "Provide a detailed technical explanation of this code, including algorithms, design patterns, and performance considerations."
        }
        
        prompt = f"""
        {complexity_prompts[complexity_level]}
        
        Programming Language: {programming_language}
        
        Code to explain:
        ```{programming_language.lower()}
        {code_snippet}
        ```
        
        Please provide:
        1. A brief overview of what the code does
        2. Step-by-step explanation of each part
        3. Key concepts or techniques used
        4. Any potential improvements or considerations (if applicable)
        
        Format your response in a clear, easy-to-read manner.
        """
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programming instructor who excels at explaining code in clear, understandable language. Always be encouraging and educational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama3-8b-8192",  # You can change this to other Groq models
            temperature=0.3,
            max_tokens=1500,
        )
        
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        return f"Error explaining code: {str(e)}"

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Code Explainer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar for API key and settings
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key input
        api_key = st.secrets.get("GROQ_API_KEY")
            
        
        if api_key:
            st.session_state['groq_api_key'] = api_key
            st.success("API Key saved!")
        
        st.markdown("---")
        
        # Language selection
        programming_language = st.selectbox(
            "Programming Language",
            ["Python", "JavaScript", "Java", "C++", "C", "C#", "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Other"]
        )
        
        # Complexity level
        complexity_level = st.selectbox(
            "Explanation Level",
            ["Beginner", "Intermediate", "Advanced"],
            help="Choose the complexity level for the explanation"
        )
        
        st.markdown("---")
        st.markdown("### 📝 Sample Code")
        
        # Sample code buttons
        if st.button("Python List Comprehension"):
            st.session_state['sample_code'] = """numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
even_squares = [x**2 for x in numbers if x % 2 == 0]
print(even_squares)"""
        
        if st.button("JavaScript Function"):
            st.session_state['sample_code'] = """function fibonacci(n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

console.log(fibonacci(10));"""
        
        if st.button("Python Class"):
            st.session_state['sample_code'] = """class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
        
calc = Calculator()
print(calc.add(5, 3))"""

    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📋 Code Input")
        
        # Code input area
        code_snippet = st.text_area(
            "Paste your code here:",
            height=400,
            value=st.session_state.get('sample_code', ''),
            placeholder="Enter your code snippet here...",
            help="Paste the code you want explained"
        )
        
        # Clear button
        if st.button("Clear Code", type="secondary"):
            st.session_state['sample_code'] = ''
            st.rerun()
    
    with col2:
        st.header("💡 Code Explanation")
        
        if st.button("Explain Code", type="primary", use_container_width=True):
            if not code_snippet.strip():
                st.warning("Please enter some code to explain!")
            elif not st.session_state.get('groq_api_key'):
                st.error("Please enter your Groq API key in the sidebar!")
            else:
                client = initialize_groq_client()
                if client:
                    with st.spinner("Analyzing your code..."):
                        explanation = explain_code(
                            client, 
                            code_snippet, 
                            programming_language, 
                            complexity_level
                        )
                        
                        st.markdown('<div class="explanation-container">', unsafe_allow_html=True)
                        st.markdown(explanation)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.error("Failed to initialize Groq client. Please check your API key.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit and Groq Cloud API</p>
        <p><strong>Tips:</strong> Start with simple code snippets • Try different explanation levels • Use the sample code buttons</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
