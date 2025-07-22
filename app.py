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
    
    # Enhanced Custom CSS for modern, professional styling
    custom_css = """
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* CSS Variables for Theme Support */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --success-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --warning-gradient: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        --glass-bg: rgba(255, 255, 255, 0.95);
        --glass-border: rgba(255, 255, 255, 0.2);
        --text-primary: #2d3748;
        --text-secondary: #4a5568;
        --text-light: #718096;
        --bg-light: #f7fafc;
        --bg-card: #ffffff;
        --shadow-sm: 0 2px 10px rgba(0, 0, 0, 0.05);
        --shadow-md: 0 10px 30px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 20px 40px rgba(0, 0, 0, 0.15);
        --border-radius: 12px;
        --border-radius-lg: 20px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif !important;
        box-sizing: border-box !important;
    }
    
    /* Main Container with Enhanced Background */
    .gradio-container {
        max-width: 1400px !important;
        margin: 0 auto !important;
        background: 
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3), transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3), transparent 50%),
            radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.3), transparent 50%),
            var(--primary-gradient) !important;
        min-height: 100vh !important;
        padding: 20px !important;
        position: relative !important;
        overflow-x: hidden !important;
    }
    
    /* Animated Background Particles */
    .gradio-container::before {
        content: '' !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='7' cy='7' r='1'/%3E%3Ccircle cx='53' cy='7' r='1'/%3E%3Ccircle cx='7' cy='53' r='1'/%3E%3Ccircle cx='53' cy='53' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E") !important;
        animation: float 20s ease-in-out infinite !important;
        pointer-events: none !important;
        z-index: 0 !important;
    }
    
    /* Main Content Area with Glass Effect */
    .main-content {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-radius: var(--border-radius-lg) !important;
        box-shadow: 
            var(--shadow-lg),
            inset 0 1px 0 var(--glass-border) !important;
        padding: 40px !important;
        margin: 20px 0 !important;
        position: relative !important;
        z-index: 1 !important;
        border: 1px solid var(--glass-border) !important;
        transition: var(--transition) !important;
    }
    
    .main-content:hover {
        transform: translateY(-2px) !important;
        box-shadow: 
            0 25px 50px rgba(0, 0, 0, 0.15),
            inset 0 1px 0 var(--glass-border) !important;
    }
    
    /* Enhanced Header with Animations */
    .markdown h1 {
        background: var(--primary-gradient) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        font-size: 3rem !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 1.5rem !important;
        position: relative !important;
        animation: titleGlow 3s ease-in-out infinite alternate !important;
    }
    
    .markdown h1::after {
        content: '' !important;
        position: absolute !important;
        bottom: -10px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        width: 100px !important;
        height: 4px !important;
        background: var(--primary-gradient) !important;
        border-radius: 2px !important;
        animation: pulse 2s ease-in-out infinite !important;
    }
    
    /* Enhanced Chat Interface */
    .chatbot {
        border: none !important;
        border-radius: var(--border-radius) !important;
        box-shadow: var(--shadow-md) !important;
        background: var(--bg-card) !important;
        overflow: hidden !important;
        position: relative !important;
    }
    
    /* Chat Messages with Better Styling */
    .chatbot .message-wrap {
        padding: 20px !important;
        margin: 15px !important;
        border-radius: 18px !important;
        max-width: 85% !important;
        animation: messageSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        word-wrap: break-word !important;
    }
    
    .chatbot .message.user {
        background: var(--primary-gradient) !important;
        color: white !important;
        margin-left: auto !important;
        margin-right: 15px !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
        border-bottom-right-radius: 5px !important;
    }
    
    .chatbot .message.user::before {
        content: '🧑‍💻' !important;
        position: absolute !important;
        top: -25px !important;
        right: 10px !important;
        font-size: 16px !important;
        background: var(--bg-card) !important;
        padding: 5px 8px !important;
        border-radius: 20px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .chatbot .message.bot {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%) !important;
        color: var(--text-primary) !important;
        margin-right: auto !important;
        margin-left: 15px !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: var(--shadow-sm) !important;
        border-bottom-left-radius: 5px !important;
    }
    
    .chatbot .message.bot::before {
        content: '🤖' !important;
        position: absolute !important;
        top: -25px !important;
        left: 10px !important;
        font-size: 16px !important;
        background: var(--bg-card) !important;
        padding: 5px 8px !important;
        border-radius: 20px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Typing Indicator */
    .typing-indicator {
        display: flex !important;
        align-items: center !important;
        padding: 15px 20px !important;
        margin: 15px !important;
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%) !important;
        border-radius: 18px !important;
        max-width: 85% !important;
        margin-right: auto !important;
        margin-left: 15px !important;
        border: 1px solid #e2e8f0 !important;
        animation: messageSlideIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    .typing-dots {
        display: flex !important;
        align-items: center !important;
        gap: 4px !important;
    }
    
    .typing-dots span {
        width: 8px !important;
        height: 8px !important;
        border-radius: 50% !important;
        background: var(--text-light) !important;
        animation: typingDots 1.4s ease-in-out infinite both !important;
    }
    
    .typing-dots span:nth-child(1) { animation-delay: -0.32s !important; }
    .typing-dots span:nth-child(2) { animation-delay: -0.16s !important; }
    .typing-dots span:nth-child(3) { animation-delay: 0s !important; }
    
    /* Enhanced Input Areas */
    .textbox input, .textbox textarea {
        border: 2px solid #e2e8f0 !important;
        border-radius: var(--border-radius) !important;
        padding: 18px 24px !important;
        font-size: 16px !important;
        line-height: 1.5 !important;
        transition: var(--transition) !important;
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-sm) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .textbox input:focus, .textbox textarea:focus {
        border-color: #667eea !important;
        box-shadow: 
            0 0 0 4px rgba(102, 126, 234, 0.1),
            var(--shadow-md) !important;
        outline: none !important;
        transform: translateY(-1px) !important;
        background: #ffffff !important;
    }
    
    /* Enhanced Buttons with Micro-interactions */
    .btn {
        border-radius: var(--border-radius) !important;
        font-weight: 600 !important;
        text-transform: none !important;
        letter-spacing: 0.3px !important;
        transition: var(--transition) !important;
        border: none !important;
        box-shadow: var(--shadow-sm) !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .btn::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent) !important;
        transition: left 0.5s !important;
    }
    
    .btn:hover::before {
        left: 100% !important;
    }
    
    .btn-primary {
        background: var(--primary-gradient) !important;
        color: white !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3) !important;
    }
    
    .btn-primary:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
    }
    
    .btn-primary:active {
        transform: translateY(-1px) scale(0.98) !important;
    }
    
    .btn-secondary {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
        color: var(--text-secondary) !important;
        border: 1px solid #e2e8f0 !important;
    }
    
    .btn-secondary:hover {
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Enhanced File Upload with Drag & Drop Animation */
    .file-upload {
        border: 3px dashed #cbd5e0 !important;
        border-radius: var(--border-radius) !important;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
        padding: 40px !important;
        text-align: center !important;
        transition: var(--transition) !important;
        position: relative !important;
        overflow: hidden !important;
        cursor: pointer !important;
    }
    
    .file-upload:hover {
        border-color: #667eea !important;
        background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%) !important;
        transform: translateY(-2px) scale(1.01) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .file-upload::before {
        content: '📁' !important;
        font-size: 4rem !important;
        display: block !important;
        margin-bottom: 15px !important;
        animation: fileFloat 3s ease-in-out infinite !important;
    }
    
    .file-upload::after {
        content: 'Drag files here or click to browse' !important;
        position: absolute !important;
        bottom: 15px !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
        font-size: 14px !important;
        color: var(--text-light) !important;
        font-weight: 500 !important;
    }
    
    /* Enhanced Examples Section */
    .examples {
        background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%) !important;
        border-radius: var(--border-radius) !important;
        padding: 30px !important;
        margin: 25px 0 !important;
        border: 1px solid #e2e8f0 !important;
        box-shadow: var(--shadow-sm) !important;
        position: relative !important;
    }
    
    .examples::before {
        content: '💡' !important;
        position: absolute !important;
        top: -15px !important;
        left: 30px !important;
        background: var(--bg-card) !important;
        padding: 10px !important;
        border-radius: 50% !important;
        font-size: 20px !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .examples h3 {
        color: #667eea !important;
        font-weight: 700 !important;
        margin-bottom: 20px !important;
        font-size: 1.3rem !important;
        margin-left: 20px !important;
    }
    
    /* Feature Cards with Hover Effects */
    .feature-card {
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        padding: 25px !important;
        margin: 15px 0 !important;
        box-shadow: var(--shadow-sm) !important;
        border-left: 4px solid transparent !important;
        transition: var(--transition) !important;
        cursor: pointer !important;
    }
    
    .feature-card:hover {
        transform: translateY(-5px) translateX(5px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .feature-card.research {
        border-left-color: #667eea !important;
    }
    
    .feature-card.code {
        border-left-color: #48bb78 !important;
    }
    
    .feature-card.data {
        border-left-color: #ed8936 !important;
    }
    
    .feature-card.image {
        border-left-color: #dd6b20 !important;
    }
    
    /* Status Indicator with Pulse Animation */
    .status-indicator {
        display: inline-block !important;
        width: 12px !important;
        height: 12px !important;
        border-radius: 50% !important;
        background: radial-gradient(circle, #48bb78, #38a169) !important;
        margin-right: 12px !important;
        animation: statusPulse 2s ease-in-out infinite !important;
        box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.7) !important;
    }
    
    /* Enhanced Footer */
    .footer {
        background: var(--glass-bg) !important;
        backdrop-filter: blur(10px) !important;
        border-radius: var(--border-radius) !important;
        padding: 30px !important;
        margin-top: 40px !important;
        text-align: center !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Advanced Animations */
    @keyframes titleGlow {
        0%, 100% { text-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
        50% { text-shadow: 0 0 30px rgba(102, 126, 234, 0.8), 0 0 40px rgba(118, 75, 162, 0.6); }
    }
    
    @keyframes messageSlideIn {
        from {
            opacity: 0;
            transform: translateY(30px) scale(0.95);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }
    
    @keyframes typingDots {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1.2); opacity: 1; }
    }
    
    @keyframes fileFloat {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes statusPulse {
        0% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(72, 187, 120, 0.7);
        }
        70% {
            transform: scale(1);
            box-shadow: 0 0 0 10px rgba(72, 187, 120, 0);
        }
        100% {
            transform: scale(0.95);
            box-shadow: 0 0 0 0 rgba(72, 187, 120, 0);
        }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-10px) rotate(1deg); }
        66% { transform: translateY(-5px) rotate(-1deg); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1) scaleX(1); }
        50% { transform: scale(1.05) scaleX(1.1); }
    }
    
    /* Responsive Design Enhancements */
    @media (max-width: 1024px) {
        .gradio-container { padding: 15px !important; }
        .main-content { padding: 25px !important; margin: 15px 0 !important; }
        .markdown h1 { font-size: 2.5rem !important; }
    }
    
    @media (max-width: 768px) {
        .gradio-container { padding: 10px !important; }
        .main-content { padding: 20px !important; margin: 10px 0 !important; }
        .chatbot .message-wrap { max-width: 90% !important; margin: 10px !important; padding: 15px !important; }
        .markdown h1 { font-size: 2rem !important; }
        .btn { padding: 12px 20px !important; font-size: 14px !important; }
        .file-upload { padding: 30px 20px !important; }
    }
    
    @media (max-width: 480px) {
        .markdown h1 { font-size: 1.8rem !important; }
        .chatbot .message-wrap { margin: 8px !important; padding: 12px !important; }
        .main-content { padding: 15px !important; }
    }
    
    /* Custom Scrollbar Enhancement */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { 
        background: rgba(241, 241, 241, 0.5); 
        border-radius: 6px; 
    }
    ::-webkit-scrollbar-thumb { 
        background: var(--primary-gradient); 
        border-radius: 6px; 
        border: 2px solid rgba(255, 255, 255, 0.2);
    }
    ::-webkit-scrollbar-thumb:hover { 
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%); 
    }
    
    /* Loading States */
    .loading { animation: pulse 2s infinite !important; }
    .processing { 
        position: relative !important;
        overflow: hidden !important;
    }
    .processing::after {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent) !important;
        animation: shimmer 2s infinite !important;
    }
    
    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    /* Dark mode support (future enhancement) */
    @media (prefers-color-scheme: dark) {
        :root {
            --glass-bg: rgba(26, 32, 44, 0.95);
            --text-primary: #e2e8f0;
            --text-secondary: #cbd5e0;
            --text-light: #a0aec0;
            --bg-card: #2d3748;
            --bg-light: #1a202c;
        }
    }
    """
    
    with gr.Blocks(css=custom_css, title="GAIA Agent - Q&A Chatbot", theme=gr.themes.Soft()) as demo:
        # Header with enhanced styling
        with gr.Row(elem_classes="main-content"):
            gr.Markdown(
                """
                <h1 align="center">🤖 GAIA Agent - Advanced Q&A Chatbot</h1>
                
                Welcome to the **GAIA Agent Q&A interface**! Ask me anything and I'll help you find the answer using my various tools and capabilities.
                
                ### 🌟 **What I can do:**
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0;">
                    <div class="feature-card research" style="background: linear-gradient(135deg, #f8f9ff 0%, #e8eeff 100%); padding: 25px; border-radius: 12px; border-left: 4px solid #667eea; cursor: pointer; transition: all 0.3s ease;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 2rem; margin-right: 15px;">🔍</span>
                            <strong style="font-size: 1.1rem; color: #667eea;">Research & Search</strong>
                        </div>
                        <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Web search, Wikipedia, academic papers, arXiv research</p>
                    </div>
                    <div class="feature-card code" style="background: linear-gradient(135deg, #f0fff4 0%, #c6f6d5 100%); padding: 25px; border-radius: 12px; border-left: 4px solid #48bb78; cursor: pointer; transition: all 0.3s ease;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 2rem; margin-right: 15px;">💻</span>
                            <strong style="font-size: 1.1rem; color: #48bb78;">Code Execution</strong>
                        </div>
                        <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Python, Bash, SQL, C, Java with real-time results</p>
                    </div>
                    <div class="feature-card data" style="background: linear-gradient(135deg, #fffaf0 0%, #fbd38d 100%); padding: 25px; border-radius: 12px; border-left: 4px solid #ed8936; cursor: pointer; transition: all 0.3s ease;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 2rem; margin-right: 15px;">📊</span>
                            <strong style="font-size: 1.1rem; color: #ed8936;">Data Analysis</strong>
                        </div>
                        <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">CSV, Excel, visualizations, statistical analysis</p>
                    </div>
                    <div class="feature-card image" style="background: linear-gradient(135deg, #fef5e7 0%, #f6ad55 100%); padding: 25px; border-radius: 12px; border-left: 4px solid #dd6b20; cursor: pointer; transition: all 0.3s ease;">
                        <div style="display: flex; align-items: center; margin-bottom: 10px;">
                            <span style="font-size: 2rem; margin-right: 15px;">🖼️</span>
                            <strong style="font-size: 1.1rem; color: #dd6b20;">Image Processing</strong>
                        </div>
                        <p style="margin: 0; color: #718096; font-size: 14px; line-height: 1.5;">Analysis, OCR, transformations, generation</p>
                    </div>
                </div>
                
                ---
                """
            )
        
        # Chat interface with enhanced styling
        with gr.Row(elem_classes="main-content"):
            with gr.Column(scale=1):
                chatbot_interface = gr.Chatbot(
                    label="💬 Conversation",
                    height=600,
                    show_label=True,
                    container=True,
                    bubble_full_width=False,
                    elem_classes="chatbot"
                )
        
        # File upload section with enhanced styling
        with gr.Row(elem_classes="main-content"):
            with gr.Column():
                file_upload = gr.File(
                    label="📁 Upload Files - Drag & drop or click to upload images, documents, CSV, Excel files, etc.",
                    file_count="multiple",
                    file_types=[
                        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",  # Images
                        ".txt", ".md", ".py", ".js", ".html", ".css", ".json", ".xml",  # Text files
                        ".csv", ".xlsx", ".xls",  # Data files
                        ".pdf", ".doc", ".docx"  # Documents
                    ],
                    height=120,
                    elem_classes="file-upload"
                )
        
        # Input and buttons with enhanced styling
        with gr.Row(elem_classes="main-content"):
            with gr.Column(scale=8):
                question_input = gr.Textbox(
                    label="💭 Ask a question",
                    placeholder="Type your question here or upload files above... (e.g., 'What is the capital of France?', 'Analyze this image', 'Summarize this document')",
                    lines=3,
                    max_lines=5,
                    elem_classes="textbox"
                )
            with gr.Column(scale=2, min_width=120):
                submit_btn = gr.Button("🚀 Send", variant="primary", size="lg", elem_classes="btn btn-primary")
        
        with gr.Row(elem_classes="main-content"):
            with gr.Column(scale=1):
                clear_btn = gr.Button("🧹 Clear History", variant="secondary", elem_classes="btn btn-secondary")
            with gr.Column(scale=1):
                clear_files_btn = gr.Button("🗑️ Clear Files", variant="secondary", elem_classes="btn btn-secondary")
            with gr.Column(scale=1):
                export_btn = gr.Button("💾 Export Chat", variant="secondary", elem_classes="btn btn-secondary")
                
        # Hidden download component for chat export
        download_file = gr.File(visible=False)
            
        with gr.Row(elem_classes="main-content"):
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
                    label="🌐 General Questions"
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
                    label="🔬 Research & Analysis"
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
                    label="📁 File Analysis"
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
            
        def export_conversation(history):
            """Export conversation history to a text file"""
            print("💾 UI: Export conversation button clicked")
            if not history:
                print("⚠️  No conversation to export")
                return None
                
            try:
                import tempfile
                import datetime
                
                # Create export content
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                export_content = f"# GAIA Agent Conversation Export\n"
                export_content += f"Export Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                export_content += f"Total Messages: {len(history)}\n\n"
                export_content += "=" * 50 + "\n\n"
                
                for i, (user_msg, bot_msg) in enumerate(history, 1):
                    export_content += f"## Message {i}\n\n"
                    export_content += f"**User:** {user_msg}\n\n"
                    export_content += f"**Assistant:** {bot_msg}\n\n"
                    export_content += "-" * 30 + "\n\n"
                
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w', 
                    suffix=f'_gaia_chat_export_{timestamp}.md',
                    delete=False,
                    encoding='utf-8'
                )
                temp_file.write(export_content)
                temp_file.close()
                
                print(f"📄 Conversation exported to: {temp_file.name}")
                return temp_file.name
                
            except Exception as e:
                print(f"❌ Error exporting conversation: {e}")
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
        
        export_btn.click(
            fn=export_conversation,
            inputs=[chatbot_interface],
            outputs=[download_file],
            show_progress=True
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