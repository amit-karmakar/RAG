# RAG
#  How to Run the RAG-based FastAPI Project
This guide explains how to run the Retrieval-Augmented Generation (RAG) FastAPI app on your local machine using **VS Code** or any terminal.
##  Prerequisites
!. The things you should need for the project
- Python 3.8 or above
- Git (optional)
- Virtual environment (recommended)
2. Create & Activate Virtual Environment
  python -m venv venv
.\venv\Scripts\activate(for windows)
3. Install Dependencies
  pip install -r requirements.txt
4. Add OpenAI API Key
  Create a .env file in the root folder:OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx(put your api key here)
5. Start the FastAPI Server
  uvicorn main:app --reload
