import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
import tempfile
import re
import json
import requests
from urllib.parse import urlparse
import pytesseract
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import cmath
import pandas as pd
import uuid
import numpy as np
from code_interpreter import CodeInterpreter

interpreter_instance = CodeInterpreter()

from image_processing import *

"""Langraph"""
from langgraph.graph import START, StateGraph, MessagesState
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import WikipediaLoader
from langchain_community.document_loaders import ArxivLoader
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_huggingface import (
    ChatHuggingFace,
    HuggingFaceEndpoint,
    HuggingFaceEmbeddings,
)
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool
from langchain.tools.retriever import create_retriever_tool
from supabase.client import Client, create_client

load_dotenv()

### =============== BROWSER TOOLS =============== ###


@tool
def wiki_search(query: str) -> str:
    """Search Wikipedia for a query and return maximum 2 results.

    Args:
        query: The search query."""
    search_docs = WikipediaLoader(query=query, load_max_docs=2).load()
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"wiki_results": formatted_search_docs}


@tool
def web_search(query: str) -> str:
    """Search Tavily for a query and return maximum 3 results.

    Args:
        query: The search query."""
    search_docs = TavilySearchResults(max_results=3).invoke(query)
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.get("url", "")}" title="{doc.get("title", "")}"/>\n{doc.get("content", "")}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"web_results": formatted_search_docs}


@tool
def arxiv_search(query: str) -> str:
    """Search Arxiv for a query and return maximum 3 result.

    Args:
        query: The search query."""
    search_docs = ArxivLoader(query=query, load_max_docs=3).load()
    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content[:1000]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"arxiv_results": formatted_search_docs}


### =============== CODE INTERPRETER TOOLS =============== ###


@tool
def execute_code_multilang(code: str, language: str = "python") -> str:
    """Execute code in multiple languages (Python, Bash, SQL, C, Java) and return results.

    Args:
        code (str): The source code to execute.
        language (str): The language of the code. Supported: "python", "bash", "sql", "c", "java".

    Returns:
        A string summarizing the execution results (stdout, stderr, errors, plots, dataframes if any).
    """
    supported_languages = ["python", "bash", "sql", "c", "java"]
    language = language.lower()

    if language not in supported_languages:
        return f"❌ Unsupported language: {language}. Supported languages are: {', '.join(supported_languages)}"

    result = interpreter_instance.execute_code(code, language=language)

    response = []

    if result["status"] == "success":
        response.append(f"✅ Code executed successfully in **{language.upper()}**")

        if result.get("stdout"):
            response.append(
                "\n**Standard Output:**\n```\n" + result["stdout"].strip() + "\n```"
            )

        if result.get("stderr"):
            response.append(
                "\n**Standard Error (if any):**\n```\n"
                + result["stderr"].strip()
                + "\n```"
            )

        if result.get("result") is not None:
            response.append(
                "\n**Execution Result:**\n```\n"
                + str(result["result"]).strip()
                + "\n```"
            )

        if result.get("dataframes"):
            for df_info in result["dataframes"]:
                response.append(
                    f"\n**DataFrame `{df_info['name']}` (Shape: {df_info['shape']})**"
                )
                df_preview = pd.DataFrame(df_info["head"])
                response.append("First 5 rows:\n```\n" + str(df_preview) + "\n```")

        if result.get("plots"):
            response.append(
                f"\n**Generated {len(result['plots'])} plot(s)** (Image data returned separately)"
            )

    else:
        response.append(f"❌ Code execution failed in **{language.upper()}**")
        if result.get("stderr"):
            response.append(
                "\n**Error Log:**\n```\n" + result["stderr"].strip() + "\n```"
            )

    return "\n".join(response)


### =============== MATHEMATICAL TOOLS =============== ###


@tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers.

    Args:
        a (float): the first number
        b (float): the second number
    """
    return a * b


@tool
def add(a: float, b: float) -> float:
    """
    Adds two numbers.

    Args:
        a (float): the first number
        b (float): the second number
    """
    return a + b


@tool
def subtract(a: float, b: float) -> int:
    """
    Subtracts two numbers.

    Args:
        a (float): the first number
        b (float): the second number
    """
    return a - b


@tool
def divide(a: float, b: float) -> float:
    """
    Divides two numbers.

    Args:
        a (float): the first float number
        b (float): the second float number
    """
    if b == 0:
        raise ValueError("Cannot divided by zero.")
    return a / b


@tool
def modulus(a: int, b: int) -> int:
    """
    Get the modulus of two numbers.

    Args:
        a (int): the first number
        b (int): the second number
    """
    return a % b


@tool
def power(a: float, b: float) -> float:
    """
    Get the power of two numbers.

    Args:
        a (float): the first number
        b (float): the second number
    """
    return a**b


@tool
def square_root(a: float) -> float | complex:
    """
    Get the square root of a number.

    Args:
        a (float): the number to get the square root of
    """
    if a >= 0:
        return a**0.5
    return cmath.sqrt(a)


### =============== DOCUMENT PROCESSING TOOLS =============== ###


@tool
def save_and_read_file(content: str, filename: Optional[str] = None) -> str:
    """
    Save content to a file and return the path.

    Args:
        content (str): the content to save to the file
        filename (str, optional): the name of the file. If not provided, a random name file will be created.
    """
    temp_dir = tempfile.gettempdir()
    if filename is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, dir=temp_dir)
        filepath = temp_file.name
    else:
        filepath = os.path.join(temp_dir, filename)

    with open(filepath, "w") as f:
        f.write(content)

    return f"File saved to {filepath}. You can read this file to process its contents."


@tool
def download_file_from_url(url: str, filename: Optional[str] = None) -> str:
    """
    Download a file from a URL and save it to a temporary location.

    Args:
        url (str): the URL of the file to download.
        filename (str, optional): the name of the file. If not provided, a random name file will be created.
    """
    try:
        # Parse URL to get filename if not provided
        if not filename:
            path = urlparse(url).path
            filename = os.path.basename(path)
            if not filename:
                filename = f"downloaded_{uuid.uuid4().hex[:8]}"

        # Create temporary file
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)

        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Save the file
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"File downloaded to {filepath}. You can read this file to process its contents."
    except Exception as e:
        return f"Error downloading file: {str(e)}"


@tool
def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using OCR library pytesseract (if available).

    Args:
        image_path (str): the path to the image file.
    """
    try:
        # Open the image
        image = Image.open(image_path)

        # Extract text from the image
        text = pytesseract.image_to_string(image)

        return f"Extracted text from image:\n\n{text}"
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"


@tool
def analyze_csv_file(file_path: str, query: str) -> str:
    """
    Analyze a CSV file using pandas and answer a question about it.

    Args:
        file_path (str): the path to the CSV file.
        query (str): Question about the data
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Run various analyses based on the query
        result = f"CSV file loaded with {len(df)} rows and {len(df.columns)} columns.\n"
        result += f"Columns: {', '.join(df.columns)}\n\n"

        # Add summary statistics
        result += "Summary statistics:\n"
        result += str(df.describe())

        return result

    except Exception as e:
        return f"Error analyzing CSV file: {str(e)}"


@tool
def analyze_excel_file(file_path: str, query: str) -> str:
    """
    Analyze an Excel file using pandas and answer a question about it.

    Args:
        file_path (str): the path to the Excel file.
        query (str): Question about the data
    """
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)

        # Run various analyses based on the query
        result = (
            f"Excel file loaded with {len(df)} rows and {len(df.columns)} columns.\n"
        )
        result += f"Columns: {', '.join(df.columns)}\n\n"

        # Add summary statistics
        result += "Summary statistics:\n"
        result += str(df.describe())

        return result

    except Exception as e:
        return f"Error analyzing Excel file: {str(e)}"


### ============== IMAGE PROCESSING AND GENERATION TOOLS =============== ###


@tool
def analyze_image(image_base64: str) -> Dict[str, Any]:
    """
    Analyze basic properties of an image (size, mode, color analysis, thumbnail preview).

    Args:
        image_base64 (str): Base64 encoded image string

    Returns:
        Dictionary with analysis result
    """
    try:
        img = decode_image(image_base64)
        width, height = img.size
        mode = img.mode

        if mode in ("RGB", "RGBA"):
            arr = np.array(img)
            avg_colors = arr.mean(axis=(0, 1))
            dominant = ["Red", "Green", "Blue"][np.argmax(avg_colors[:3])]
            brightness = avg_colors.mean()
            color_analysis = {
                "average_rgb": avg_colors.tolist(),
                "brightness": brightness,
                "dominant_color": dominant,
            }
        else:
            color_analysis = {"note": f"No color analysis for mode {mode}"}

        thumbnail = img.copy()
        thumbnail.thumbnail((100, 100))
        thumb_path = save_image(thumbnail, "thumbnails")
        thumbnail_base64 = encode_image(thumb_path)

        return {
            "dimensions": (width, height),
            "mode": mode,
            "color_analysis": color_analysis,
            "thumbnail": thumbnail_base64,
        }
    except Exception as e:
        return {"error": str(e)}


@tool
def transform_image(
    image_base64: str, operation: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Apply transformations: resize, rotate, crop, flip, brightness, contrast, blur, sharpen, grayscale.

    Args:
        image_base64 (str): Base64 encoded input image
        operation (str): Transformation operation
        params (Dict[str, Any], optional): Parameters for the operation

    Returns:
        Dictionary with transformed image (base64)
    """
    try:
        img = decode_image(image_base64)
        params = params or {}

        if operation == "resize":
            img = img.resize(
                (
                    params.get("width", img.width // 2),
                    params.get("height", img.height // 2),
                )
            )
        elif operation == "rotate":
            img = img.rotate(params.get("angle", 90), expand=True)
        elif operation == "crop":
            img = img.crop(
                (
                    params.get("left", 0),
                    params.get("top", 0),
                    params.get("right", img.width),
                    params.get("bottom", img.height),
                )
            )
        elif operation == "flip":
            if params.get("direction", "horizontal") == "horizontal":
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            else:
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
        elif operation == "adjust_brightness":
            img = ImageEnhance.Brightness(img).enhance(params.get("factor", 1.5))
        elif operation == "adjust_contrast":
            img = ImageEnhance.Contrast(img).enhance(params.get("factor", 1.5))
        elif operation == "blur":
            img = img.filter(ImageFilter.GaussianBlur(params.get("radius", 2)))
        elif operation == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        elif operation == "grayscale":
            img = img.convert("L")
        else:
            return {"error": f"Unknown operation: {operation}"}

        result_path = save_image(img)
        result_base64 = encode_image(result_path)
        return {"transformed_image": result_base64}

    except Exception as e:
        return {"error": str(e)}


@tool
def draw_on_image(
    image_base64: str, drawing_type: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Draw shapes (rectangle, circle, line) or text onto an image.

    Args:
        image_base64 (str): Base64 encoded input image
        drawing_type (str): Drawing type
        params (Dict[str, Any]): Drawing parameters

    Returns:
        Dictionary with result image (base64)
    """
    try:
        img = decode_image(image_base64)
        draw = ImageDraw.Draw(img)
        color = params.get("color", "red")

        if drawing_type == "rectangle":
            draw.rectangle(
                [params["left"], params["top"], params["right"], params["bottom"]],
                outline=color,
                width=params.get("width", 2),
            )
        elif drawing_type == "circle":
            x, y, r = params["x"], params["y"], params["radius"]
            draw.ellipse(
                (x - r, y - r, x + r, y + r),
                outline=color,
                width=params.get("width", 2),
            )
        elif drawing_type == "line":
            draw.line(
                (
                    params["start_x"],
                    params["start_y"],
                    params["end_x"],
                    params["end_y"],
                ),
                fill=color,
                width=params.get("width", 2),
            )
        elif drawing_type == "text":
            font_size = params.get("font_size", 20)
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            draw.text(
                (params["x"], params["y"]),
                params.get("text", "Text"),
                fill=color,
                font=font,
            )
        else:
            return {"error": f"Unknown drawing type: {drawing_type}"}

        result_path = save_image(img)
        result_base64 = encode_image(result_path)
        return {"result_image": result_base64}

    except Exception as e:
        return {"error": str(e)}


@tool
def generate_simple_image(
    image_type: str,
    width: int = 500,
    height: int = 500,
    params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate a simple image (gradient, noise, pattern, chart).

    Args:
        image_type (str): Type of image
        width (int), height (int)
        params (Dict[str, Any], optional): Specific parameters

    Returns:
        Dictionary with generated image (base64)
    """
    try:
        params = params or {}

        if image_type == "gradient":
            direction = params.get("direction", "horizontal")
            start_color = params.get("start_color", (255, 0, 0))
            end_color = params.get("end_color", (0, 0, 255))

            img = Image.new("RGB", (width, height))
            draw = ImageDraw.Draw(img)

            if direction == "horizontal":
                for x in range(width):
                    r = int(
                        start_color[0] + (end_color[0] - start_color[0]) * x / width
                    )
                    g = int(
                        start_color[1] + (end_color[1] - start_color[1]) * x / width
                    )
                    b = int(
                        start_color[2] + (end_color[2] - start_color[2]) * x / width
                    )
                    draw.line([(x, 0), (x, height)], fill=(r, g, b))
            else:
                for y in range(height):
                    r = int(
                        start_color[0] + (end_color[0] - start_color[0]) * y / height
                    )
                    g = int(
                        start_color[1] + (end_color[1] - start_color[1]) * y / height
                    )
                    b = int(
                        start_color[2] + (end_color[2] - start_color[2]) * y / height
                    )
                    draw.line([(0, y), (width, y)], fill=(r, g, b))

        elif image_type == "noise":
            noise_array = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
            img = Image.fromarray(noise_array, "RGB")

        else:
            return {"error": f"Unsupported image_type {image_type}"}

        result_path = save_image(img)
        result_base64 = encode_image(result_path)
        return {"generated_image": result_base64}

    except Exception as e:
        return {"error": str(e)}


@tool
def combine_images(
    images_base64: List[str], operation: str, params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Combine multiple images (collage, stack, blend).

    Args:
        images_base64 (List[str]): List of base64 images
        operation (str): Combination type
        params (Dict[str, Any], optional)

    Returns:
        Dictionary with combined image (base64)
    """
    try:
        images = [decode_image(b64) for b64 in images_base64]
        params = params or {}

        if operation == "stack":
            direction = params.get("direction", "horizontal")
            if direction == "horizontal":
                total_width = sum(img.width for img in images)
                max_height = max(img.height for img in images)
                new_img = Image.new("RGB", (total_width, max_height))
                x = 0
                for img in images:
                    new_img.paste(img, (x, 0))
                    x += img.width
            else:
                max_width = max(img.width for img in images)
                total_height = sum(img.height for img in images)
                new_img = Image.new("RGB", (max_width, total_height))
                y = 0
                for img in images:
                    new_img.paste(img, (0, y))
                    y += img.height
        else:
            return {"error": f"Unsupported combination operation {operation}"}

        result_path = save_image(new_img)
        result_base64 = encode_image(result_path)
        return {"combined_image": result_base64}

    except Exception as e:
        return {"error": str(e)}


# load the system prompt from the file
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    system_prompt = f.read()
print(system_prompt)

# System message
sys_msg = SystemMessage(content=system_prompt)

# build a retriever
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-mpnet-base-v2"
)  #  dim=768
supabase: Client = create_client(
    os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)
vector_store = SupabaseVectorStore(
    client=supabase,
    embedding=embeddings,
    table_name="documents2",
    query_name="match_documents_2",
)
create_retriever_tool = create_retriever_tool(
    retriever=vector_store.as_retriever(),
    name="Question Search",
    description="A tool to retrieve similar questions from a vector store.",
)


tools = [
    web_search,
    wiki_search,
    arxiv_search,
    multiply,
    add,
    subtract,
    divide,
    modulus,
    power,
    square_root,
    save_and_read_file,
    download_file_from_url,
    extract_text_from_image,
    analyze_csv_file,
    analyze_excel_file,
    execute_code_multilang,
    analyze_image,
    transform_image,
    draw_on_image,
    generate_simple_image,
    combine_images,
]


# Build graph function
def build_graph(provider: str = "groq"):
    """Build the graph"""
    # Load environment variables from .env file
    if provider == "groq":
        # Groq https://console.groq.com/docs/models
        llm = ChatGroq(model="qwen/qwen3-32b", temperature=0)
    elif provider == "huggingface":
        # TODO: Add huggingface endpoint
        llm = ChatHuggingFace(
            llm=HuggingFaceEndpoint(
                repo_id="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                task="text-generation",  # for chat‐style use “text-generation”
                max_new_tokens=1024,
                do_sample=False,
                repetition_penalty=1.03,
                temperature=0,
            ),
            verbose=True,
        )
    else:
        raise ValueError("Invalid provider. Choose 'groq' or 'huggingface'.")
    # Bind tools to LLM
    llm_with_tools = llm.bind_tools(tools)

    # Node
    def assistant(state: MessagesState):
        """Assistant node"""
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    def retriever(state: MessagesState):
        """Retriever node"""
        similar_question = vector_store.similarity_search(state["messages"][0].content)

        if similar_question:  # Check if the list is not empty
            example_msg = HumanMessage(
                content=f"Here I provide a similar question and answer for reference: \n\n{similar_question[0].page_content}",
            )
            return {"messages": [sys_msg] + state["messages"] + [example_msg]}
        else:
            # Handle the case when no similar questions are found
            return {"messages": [sys_msg] + state["messages"]}

    builder = StateGraph(MessagesState)
    builder.add_node("retriever", retriever)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "retriever")
    builder.add_edge("retriever", "assistant")
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    # Compile graph
    return builder.compile()


# test
if __name__ == "__main__":
    question = "When was a picture of St. Thomas Aquinas first added to the Wikipedia page on the Principle of double effect?"
    graph = build_graph(provider="groq")
    messages = [HumanMessage(content=question)]
    messages = graph.invoke({"messages": messages})
    for m in messages["messages"]:
        m.pretty_print()
