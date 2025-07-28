# Adobe Connecting the Dots – Round 1B Submission
🎯 Problem Statement: Persona-driven Document Intelligence The objective of Round 1B is to develop a system that can provide persona-driven content recommendations from research papers. Given a research paper and a target persona (e.g., high school student, policy-maker, graduate researcher), the system must extract relevant information and generate a concise, persona-specific summary.

# 🛠️ Solution Overview We created a persona-aware PDF summarization engine that:

Parses the document into manageable chunks. Generates embeddings using the all-MiniLM-L6-v2 SentenceTransformer. Accepts a persona query. Ranks and selects the most relevant text spans. Returns a condensed summary tailored to the input persona. This solution is containerized using Docker for cross-platform portability.

📂 Project Structure round1b/ │ ├── input/ # Folder containing the input PDF │ └── research_paper.pdf │ ├── output/ # Folder where persona-specific summary is saved │ └── research_paper_summary.txt │ ├── model/ # Pre-downloaded SentenceTransformer model │ └── all-MiniLM-L6-v2/ │ ├── main.py # Main pipeline script ├── save_model.py # Script to download & save the embedding model ├── requirements.txt # Python package dependencies ├── Dockerfile # Docker container definition └── README.md # Project documentation

yaml Copy Edit

# 🚀 How to Run (Locally)

✅ Install Dependencies in a Virtual Environment python -m venv venv source venv/bin/activate # or venv\Scripts\activate on Windows pip install -r requirements.txt 📥 Download the SentenceTransformer Model python save_model.py This will create the folder model/all-MiniLM-L6-v2 with the necessary weights.
🧪 Run the Summarization Script Ensure a .pdf file is in the input/ directory. Then run: python main.py The persona query will be prompted via the terminal.

Output will be saved in the output/ folder as a .txt file.

# 🐳 Run with Docker

Build the Docker Image docker build -t round1b-extractor . Run the Container docker run --rm
-v "$(pwd)/input:/app/input"
-v "$(pwd)/output:/app/output"
-v "$(pwd)/model:/app/model"
--network host
# round1b-extractor 🪟 For Windows PowerShell Users:

docker run --rm -v "${PWD}/input:/app/input" -v "${PWD}/output:/app/output" -v "${PWD}/model:/app/model" --network host ` round1b-extractor 🧠 How It Works Chunking: Break the PDF into small paragraph segments.

Embedding: Encode each chunk and persona query using the all-MiniLM-L6-v2 model.

Similarity Matching: Rank chunks by cosine similarity.

Summary Generation: Return top N segments as a tailored summary.

# 📌 Dependencies sentence-transformers

PyMuPDF

torch

numpy

📋 See requirements.txt for exact versions.

📥 Sample Output Input: research_paper.pdf Persona: "Explain this paper to a high school student."

# Output:

output/research_paper_summary.txt Sample contents:

arduino Copy Edit This research explores the use of AI in understanding human language. It teaches computers to read and find important patterns in text... 🧪 Evaluation Criteria ✅ Persona relevance and clarity of summary

✅ Ability to extract useful context from complex research papers

✅ Accuracy and fluency of generated content

👨‍💻 Author Built with ❤️ by Ashutosh Bhardwaj for the Adobe Connecting the Dots Challenge – Round 1B
