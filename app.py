import gradio as gr
import time
import os
import base64
from typing import List, Tuple, Optional
from langchain_core.messages import HumanMessage
from agent import build_graph

class QnAChatbot:
    """A Q&A chatbot interface for the agent."""
    
    def __init__(self):
        print("🤖 QnAChatbot initializing...")
        print("🔧 Building agent graph...")
        self.graph = build_graph()
        self.conversation_history = []
        print("✅ QnAChatbot initialized successfully")
    
    def process_question(self, question: str, history: List[Tuple[str, str]], uploaded_files: Optional[List] = None) -> Tuple[str, List[Tuple[str, str]]]:
        """Process a question and return the response with updated history."""
        if not question.strip() and not uploaded_files:
            print("⚠️  No question or files provided")
            return "", history
        
        try:
            print(f"\n{'='*60}")
            print(f"🤖 Processing new question...")
            print(f"📝 Question: {question[:100]}{'...' if len(question) > 100 else ''}")
            print(f"📁 Files uploaded: {len(uploaded_files) if uploaded_files else 0}")
            
            # Handle uploaded files
            file_context = ""
            if uploaded_files:
                print(f"📂 Processing {len(uploaded_files)} uploaded file(s)...")
                file_context = self._process_uploaded_files(uploaded_files)
                if file_context:
                    original_question = question
                    question = f"{question}\n\n{file_context}" if question.strip() else file_context
                    print(f"📋 File context added to question (length: {len(file_context)} chars)")
            
            # Wrap the question in a HumanMessage
            messages = [HumanMessage(content=question)]
            print(f"🔄 Invoking agent graph...")
            
            # Get response from the agent
            result = self.graph.invoke({"messages": messages})
            print(f"📨 Received {len(result['messages'])} message(s) from agent")
            
            # Print all messages for debugging
            for i, msg in enumerate(result['messages']):
                print(f"📧 Message {i+1}: {type(msg).__name__}")
                if hasattr(msg, 'content'):
                    content_preview = msg.content[:200] + "..." if len(msg.content) > 200 else msg.content
                    print(f"   Content preview: {content_preview}")
            
            answer = result['messages'][-1].content
            
            # Clean up the answer if it starts with "Assistant: "
            if answer.startswith("Assistant: "):
                answer = answer[11:]
                print("🧹 Cleaned 'Assistant: ' prefix from response")
            
            # Update conversation history
            history.append((question, answer))
            print(f"✅ Question processed successfully")
            print(f"📊 Response length: {len(answer)} characters")
            print(f"💬 Total conversation history: {len(history)} exchanges")
            print(f"{'='*60}\n")
            
            return "", history
            
        except Exception as e:
            error_msg = f"Error processing question: {str(e)}"
            print(f"❌ {error_msg}")
            print(f"🔍 Exception details: {type(e).__name__}: {str(e)}")
            import traceback
            print(f"📋 Traceback:\n{traceback.format_exc()}")
            history.append((question, error_msg))
            print(f"{'='*60}\n")
            return "", history
    
    def _process_uploaded_files(self, uploaded_files: List) -> str:
        """Process uploaded files and return context for the question."""
        file_contexts = []
        
        for file_path in uploaded_files:
            if not file_path or not os.path.exists(file_path):
                print(f"⚠️  Skipping invalid file path: {file_path}")
                continue
                
            try:
                file_name = os.path.basename(file_path)
                file_ext = os.path.splitext(file_name)[1].lower()
                file_size = os.path.getsize(file_path)
                
                print(f"📄 Processing file: {file_name} ({file_size} bytes, {file_ext})")
                
                # Handle different file types
                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                    # Image file - convert to base64
                    with open(file_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                    file_contexts.append(f"[UPLOADED IMAGE: {file_name}] - Base64 data: {image_data}")
                    print(f"🖼️  Image converted to base64 ({len(image_data)} chars)")
                    
                elif file_ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml']:
                    # Text file - read content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    file_contexts.append(f"[UPLOADED TEXT FILE: {file_name}]\nContent:\n{content}")
                    print(f"📝 Text file content read ({len(content)} chars)")
                    
                elif file_ext in ['.csv']:
                    # CSV file - provide file path for analysis
                    file_contexts.append(f"[UPLOADED CSV FILE: {file_name}] - File path: {file_path}")
                    print(f"📊 CSV file prepared for analysis")
                    
                elif file_ext in ['.xlsx', '.xls']:
                    # Excel file - provide file path for analysis
                    file_contexts.append(f"[UPLOADED EXCEL FILE: {file_name}] - File path: {file_path}")
                    print(f"📈 Excel file prepared for analysis")
                    
                elif file_ext in ['.pdf']:
                    # PDF file - mention it's available
                    file_contexts.append(f"[UPLOADED PDF FILE: {file_name}] - File path: {file_path}")
                    print(f"📄 PDF file prepared for processing")
                    
                else:
                    # Other file types - just mention the file
                    file_contexts.append(f"[UPLOADED FILE: {file_name}] - File path: {file_path}")
                    print(f"📁 Generic file prepared for processing")
                    
            except Exception as e:
                error_msg = f"Error processing file {file_path}: {e}"
                print(f"❌ {error_msg}")
                print(f"🔍 File processing error details: {type(e).__name__}: {str(e)}")
                file_contexts.append(f"[ERROR PROCESSING FILE: {os.path.basename(file_path)}] - {str(e)}")
        
        total_context = "\n\n".join(file_contexts) if file_contexts else ""
        if total_context:
            print(f"📋 Total file context generated: {len(total_context)} characters")
        
        return total_context
    
    def clear_history(self):
        """Clear the conversation history."""
        print("🧹 Clearing conversation history...")
        self.conversation_history = []
        print("✅ Conversation history cleared")
        return []

def create_qna_interface():
    """Create the Q&A chatbot interface."""
    
    print("🚀 Creating Q&A interface...")
    # Initialize the chatbot
    chatbot = QnAChatbot()
    print("🎨 Setting up UI components...")
    
    # Custom CSS for better styling
    custom_css = """
    .gradio-container {
        max-width: 1200px !important;
        margin: auto !important;
    }
    .chat-message {
        padding: 10px !important;
        margin: 5px 0 !important;
        border-radius: 10px !important;
    }
    .user-message {
        background-color: #e3f2fd !important;
        margin-left: 20% !important;
    }
    .bot-message {
        background-color: #f5f5f5 !important;
        margin-right: 20% !important;
    }
    """
    
    with gr.Blocks(css=custom_css, title="GAIA Agent - Q&A Chatbot") as demo:
        gr.Markdown(
            """
            # 🤖 GAIA Agent - Q&A Chatbot
            
            Welcome to the GAIA Agent Q&A interface! Ask me anything and I'll help you find the answer using my various tools and capabilities.
            
            **What I can do:**
            - 🔍 Search the web, Wikipedia, and academic papers
            - 🧮 Perform mathematical calculations
            - 💻 Execute code in multiple languages (Python, Bash, SQL, C, Java)
            - 📊 Analyze CSV and Excel files
            - 🖼️ Process and analyze images (JPG, PNG, GIF, etc.)
            - 📄 Extract text from images (OCR)
            - 📁 Handle file uploads and processing (PDF, DOC, TXT, etc.)
            - 📈 Create visualizations and charts
            - 🔧 Multi-file analysis and comparison
            - And much more!
            
            ---
            """
        )
        
        # Chat interface
        with gr.Row():
            with gr.Column(scale=1):
                chatbot_interface = gr.Chatbot(
                    label="Conversation",
                    height=500,
                    show_label=True,
                    container=True,
                    bubble_full_width=False
                )
        
        # File upload section
        with gr.Row():
            with gr.Column():
                file_upload = gr.File(
                    label="📁 Upload Files (Images, Documents, CSV, Excel, etc.)",
                    file_count="multiple",
                    file_types=[
                        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",  # Images
                        ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml",  # Text files
                        ".csv", ".xlsx", ".xls",  # Data files
                        ".pdf", ".doc", ".docx"  # Documents
                    ],
                    height=100
                )
        
        with gr.Row():
            with gr.Column(scale=8):
                question_input = gr.Textbox(
                    label="Ask a question",
                    placeholder="Type your question here or upload files above... (e.g., 'What is the capital of France?', 'Analyze this image', 'Summarize this document')",
                    lines=2,
                    max_lines=5
                )
            with gr.Column(scale=1, min_width=100):
                submit_btn = gr.Button("Send", variant="primary", size="lg")
        
        with gr.Row():
            clear_btn = gr.Button("Clear History", variant="secondary")
            clear_files_btn = gr.Button("Clear Files", variant="secondary")
            
        # Example questions
        with gr.Row():
            gr.Markdown("### 💡 Example Questions:")
            
        with gr.Row():
            with gr.Column():
                gr.Examples(
                    examples=[
                        "What is the current population of Tokyo?",
                        "Calculate the square root of 144",
                        "Write a Python function to sort a list",
                        "What are the latest developments in AI?",
                        "Explain quantum computing in simple terms",
                    ],
                    inputs=question_input,
                    label="General Questions"
                )
            with gr.Column():
                gr.Examples(
                    examples=[
                        "Search for recent papers on machine learning",
                        "What is the weather like today?",
                        "Create a simple bar chart using Python",
                        "Convert 100 USD to EUR",
                        "What are the benefits of renewable energy?",
                    ],
                    inputs=question_input,
                    label="Research & Analysis"
                )
            with gr.Column():
                gr.Examples(
                    examples=[
                        "Analyze this image and describe what you see",
                        "Extract text from this image using OCR",
                        "Summarize the content of this document",
                        "Analyze the data in this CSV file",
                        "What insights can you find in this Excel file?",
                    ],
                    inputs=question_input,
                    label="File Analysis"
                )
        
        # Event handlers
        def submit_question(question, history, files):
            print(f"🎯 UI: Submit button clicked")
            print(f"📝 UI: Question length: {len(question) if question else 0}")
            print(f"📁 UI: Files count: {len(files) if files else 0}")
            result_question, result_history = chatbot.process_question(question, history, files)
            print(f"🔄 UI: Returning results and clearing files")
            return result_question, result_history, None  # Clear files after processing
        
        def clear_conversation():
            print("🧹 UI: Clear conversation button clicked")
            return chatbot.clear_history()
        
        def clear_files():
            print("🗑️  UI: Clear files button clicked")
            return None
        
        # Connect the events
        submit_btn.click(
            fn=submit_question,
            inputs=[question_input, chatbot_interface, file_upload],
            outputs=[question_input, chatbot_interface, file_upload],
            show_progress=True
        )
        
        question_input.submit(
            fn=submit_question,
            inputs=[question_input, chatbot_interface, file_upload],
            outputs=[question_input, chatbot_interface, file_upload],
            show_progress=True
        )
        
        clear_btn.click(
            fn=clear_conversation,
            outputs=[chatbot_interface],
            show_progress=False
        )
        
        clear_files_btn.click(
            fn=clear_files,
            outputs=[file_upload],
            show_progress=False
        )
        
        # Footer
        gr.Markdown(
            """
            ---
            
            **Note:** This agent uses various tools and APIs to provide comprehensive answers. 
            Processing complex questions and file analysis may take some time. Please be patient!
            
            **Supported file types:** 
            - **Images:** JPG, PNG, GIF, BMP, WebP
            - **Documents:** PDF, DOC, DOCX, TXT, MD
            - **Data files:** CSV, Excel (XLS, XLSX)
            - **Code files:** Python, JavaScript, HTML, CSS, JSON, XML
            
            **Powered by:** LangGraph, Groq, and various specialized tools
            """
        )
    
    return demo

if __name__ == "__main__":
    print("\n" + "-"*50)
    print("🚀 Starting GAIA Agent Q&A Chatbot...")
    print("-"*50 + "\n")
    
    # Create and launch the interface
    demo = create_qna_interface()
    demo.launch(
        debug=True,
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    ) 