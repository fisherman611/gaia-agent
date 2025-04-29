# **GAIA Agent**

## **Introduction**

**GAIA Agent** is an automated system built to tackle and submit solutions for the GAIA benchmark, which tests the capabilities of general-purpose AI agents on diverse and challenging tasks. These tasks require a combination of reasoning, code execution, information retrieval, data interpretation, and multimodal understanding. Powered by advanced language models (such as HuggingFace, and Groq), the agent incorporates a versatile set of tools including browser tools, code interpreter tools, mathematical tools, document processing tools, image processing and generation tools. It is designed for seamless interaction with the benchmark, offering automatic evaluation, submission, and result display through a user-friendly Gradio interface.

## **Tools Implementation**

### **Browser tools** 
- **Wikipedia Search:** Search Wikipedia for a query and return maximum 2 results.
- **Web Search:** Search the web for a query and return maximum 2 results.
- **Arxiv Search:** Search arXiv for a query and return maximum 2 results.

### **Code interpreter tools**
- **Execute Multi-programming Language:** Execute code in multiple languages (Python, Bash, SQL, C, Java) and return results.

### **Mathematical tools**
- **Multiplication Tools:** Multiplies 2 numbers 
- **Addition:** Adds 2 numbers
- **Subtraction:** Subtracts 2 numbers 
- **Division:** Divides 2 numbers 
- **Modulus:** Get the modulus of 2 numbers
- **Power:** Get the power of 2 numbers 
- **Square root:** Get the square root of a number

### **Document processing tools**
- **Save and Read File:** Save content to a file and return the path 
- **Download a File from URL:** Download a file from a URL and save it to a temporary location
- **Extract Text from Image:** Extract text from an image using OCR library pytesseract (if available)
- **Analyze CSV File:** Analyze a CSV file using pandas and answer a question about it 
- **Analyze Excel File:** Analyze an Excel file using pandas and answer a question about it

### **Image processing and generation tools**
- **Analyze Image:** Analyze basic properties of an image (size, mode, color analysis, thumbnail preview)
- **Transform Image:** Apply transformations: resize, rotate, crop, flip, brightness, contrast, blur, sharpen, grayscale
- **Draw on Image:** Draw shapes (rectangle, circle, line) or text onto an image
- **Generate Simple Image:** Generate a simple image (gradient, noise, pattern, chart)
- **Combine Images:** Combine multiple images (collage, stack, blend)


## **Installation**
Clone the repository, change the current working directory to this repository's root folder:

```
git clone https://github.com/fisherman611/gaia-agent.git
```
```
cd gaia-agent
```

Install ```requirements.txt``` (replace `3.11` with your installed Python version):

```
py -3.11 -m pip install -r requirements.txt
```

## **Environment Variables**
Store some API keys in the `.env` file and load it in your code using `load_dotenv`

```
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_SERVICE_KEY=...
HUGGINGFACEHUB_API_TOKEN=...
GROQ_API_KEY=...
```

## **Demo**
To run the application using the command line, use the following command (replace `3.11` with your installed Python version):
```
py -3.11 app.py
```

## **Resources**
- [GAIA Benchmark](https://huggingface.co/spaces/gaia-benchmark/leaderboard)
- [Hugging Face Agents Course](https://huggingface.co/agents-course)
- [Langgraph Agents](https://langchain-ai.github.io/langgraph/)


## **Contributing**
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## **License**
This project is licensed under the [MIT License](https://mit-license.org/).