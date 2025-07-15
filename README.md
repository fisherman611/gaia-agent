---
title: GAIA Agent - Q&A Chatbot
emoji: 🤖
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
hf_oauth: true
# optional, default duration is 8 hours/480 minutes. Max duration is 30 days/43200 minutes.
hf_oauth_expiration_minutes: 480
---

# 🤖 **GAIA Agent - Advanced Q&A Chatbot**

## 🌟 **Introduction**

**GAIA Agent** is a sophisticated AI-powered chatbot system designed to handle complex questions and tasks through an intuitive Q&A interface. Built on top of the GAIA benchmark framework, this agent combines advanced reasoning, code execution, web search, document processing, and multimodal understanding capabilities. The system features both a user-friendly chatbot interface and a comprehensive evaluation runner for benchmark testing.

## 🚀 **Key Features**

- **🔍 Multi-Modal Search**: Web search, Wikipedia, and arXiv paper search
- **💻 Code Execution**: Support for Python, Bash, SQL, C, and Java
- **🖼️ Image Processing**: Analysis, transformation, OCR, and generation
- **📄 Document Processing**: PDF, CSV, Excel, and text file analysis
- **📁 File Upload Support**: Handle multiple file types with drag-and-drop
- **🧮 Mathematical Operations**: Complete set of mathematical tools
- **💬 Conversational Interface**: Natural chat-based interaction
- **📊 Evaluation System**: Automated benchmark testing and submission

## 🏗️ **Project Structure**

```
gaia-agent/
├── app.py                    # Main Q&A chatbot interface
├── evaluation_app.py         # GAIA benchmark evaluation runner
├── agent.py                  # Core agent implementation with tools
├── code_interpreter.py       # Multi-language code execution
├── image_processing.py       # Image processing utilities
├── system_prompt.txt         # System prompt for the agent
├── requirements.txt          # Python dependencies
├── metadata.jsonl           # GAIA benchmark metadata
├── explore_metadata.ipynb   # Data exploration notebook
└── README.md               # This file
```

## 🛠️ **Tool Categories**

### **🌐 Browser & Search Tools**
- **Wikipedia Search**: Search Wikipedia with up to 2 results
- **Web Search**: Tavily-powered web search with up to 3 results  
- **arXiv Search**: Academic paper search with up to 3 results

### **💻 Code Interpreter Tools**
- **Multi-Language Execution**: Python, Bash, SQL, C, Java support
- **Plot Generation**: Matplotlib visualization support
- **DataFrame Analysis**: Pandas data processing
- **Error Handling**: Comprehensive error reporting

### **🧮 Mathematical Tools**
- **Basic Operations**: Add, subtract, multiply, divide
- **Advanced Functions**: Modulus, power, square root
- **Complex Numbers**: Support for complex number operations

### **📄 Document Processing Tools**
- **File Operations**: Save, read, and download files
- **CSV Analysis**: Pandas-based data analysis
- **Excel Processing**: Excel file analysis and processing
- **OCR**: Extract text from images using Tesseract

### **🖼️ Image Processing & Generation Tools**
- **Image Analysis**: Size, color, and property analysis
- **Transformations**: Resize, rotate, crop, flip, adjust brightness/contrast
- **Drawing Tools**: Add shapes, text, and annotations
- **Image Generation**: Create gradients, noise patterns, and simple graphics
- **Image Combination**: Stack and combine multiple images

## 🎯 **How to Use**

### **Q&A Chatbot Interface (app.py)**

1. **Start the Chatbot:**
   ```bash
   python app.py
   ```

2. **Access the Interface:**
   - Open `http://localhost:7860` in your browser
   - Upload files (images, documents, CSV, etc.) if needed
   - Ask questions in natural language
   - Get comprehensive answers with tool usage

3. **Supported Interactions:**
   - **Text Questions**: "What is the capital of France?"
   - **Math Problems**: "Calculate the square root of 144"
   - **Code Requests**: "Write a Python function to sort a list"
   - **Image Analysis**: Upload an image and ask "What do you see?"
   - **Data Analysis**: Upload a CSV and ask "What are the trends?"
   - **Web Search**: "What are the latest AI developments?"

### **Evaluation Runner (evaluation_app.py)**

1. **Run the Evaluation:**
   ```bash
   python evaluation_app.py
   ```

2. **Benchmark Testing:**
   - Log in with your Hugging Face account
   - Click "Run Evaluation & Submit All Answers"
   - Monitor progress as the agent processes GAIA benchmark questions
   - View results and scores automatically

## 🔧 **Technical Architecture**

### **LangGraph State Machine**
```
START → Retriever → Assistant → Tools → Assistant
                     ↑              ↓
                     └──────────────┘
```

1. **Retriever Node**: Searches vector database for similar questions
2. **Assistant Node**: LLM processes question with available tools
3. **Tools Node**: Executes selected tools (web search, code, etc.)
4. **Conditional Routing**: Dynamically routes between assistant and tools

### **Vector Database Integration**
- **Supabase Vector Store**: Stores GAIA benchmark Q&A pairs
- **Semantic Search**: Finds similar questions for context
- **HuggingFace Embeddings**: sentence-transformers/all-mpnet-base-v2

### **Multi-Modal File Support**
- **Images**: JPG, PNG, GIF, BMP, WebP
- **Documents**: PDF, DOC, DOCX, TXT, MD
- **Data**: CSV, Excel, JSON
- **Code**: Python, Bash, SQL, C, Java

## ⚙️ **Installation & Setup**

### **1. Clone Repository**
```bash
git clone https://github.com/fisherman611/gaia-agent.git
cd gaia-agent
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Environment Variables**
Create a `.env` file with your API keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
HUGGINGFACEHUB_API_TOKEN=your_hf_token
LANGSMITH_API_KEY=your_langsmith_key

LANGSMITH_TRACING=true
LANGSMITH_PROJECT=ai_agent_course
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

### **4. Database Setup (Supabase)**
Execute this SQL in your Supabase database:
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create match function for documents2 table
CREATE OR REPLACE FUNCTION public.match_documents_2(
  query_embedding vector(768)
)
RETURNS TABLE(
  id         bigint,
  content    text,
  metadata   jsonb,
  embedding  vector(768),
  similarity double precision
)
LANGUAGE sql STABLE
AS $$
  SELECT
    id,
    content,
    metadata,
    embedding,
    1 - (embedding <=> query_embedding) AS similarity
  FROM public.documents2
  ORDER BY embedding <=> query_embedding
  LIMIT 10;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION public.match_documents_2(vector) TO anon, authenticated;
```

## 🚀 **Running the Application**

### **Chatbot Interface**
```bash
python app.py
```
Access at: `http://localhost:7860`

### **Evaluation Runner**
```bash
python evaluation_app.py
```
Access at: `http://localhost:7860`

### **Live Demo**
Try it online: [Hugging Face Space](https://huggingface.co/spaces/fisherman611/gaia-agent)

## 🔗 **Resources**

- [GAIA Benchmark](https://huggingface.co/spaces/gaia-benchmark/leaderboard)
- [Hugging Face Agents Course](https://huggingface.co/agents-course)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Supabase Vector Store](https://supabase.com/docs/guides/ai/vector-columns)

## 🤝 **Contributing**

Contributions are welcome! Areas for improvement:
- **New Tools**: Add specialized tools for specific domains
- **UI Enhancements**: Improve the chatbot interface
- **Performance**: Optimize response times and accuracy
- **Documentation**: Expand examples and use cases

## 📄 **License**

This project is licensed under the [MIT License](https://mit-license.org/).
