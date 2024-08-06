# Rag Osint Passive reconnaissance 🕵️‍♂️

> [!WARNING]
> This Tool Is For Educational Purposes Only, Please don't use this for malicious purposes!

## 1. Introduction:

Welcome to the RAG OSINT Tool 🔍 Demo repository! This Demo showcases a sophisticated tool designed for **Open Source Intelligence (OSINT)**, utilizing Retrieval-Augmented Generation (RAG) to enhance data collection and analysis from publicly available online sources. This demo is intended to provide a clear understanding of the capabilities and potential of our RAG OSINT tool.

## 2. Key Features:

   - [x] 🌐 **Advanced Data Collection:** Utilize RAG to efficiently gather data from a multitude of online sources.
   - [x] 🧠 **Enhanced Data Analysis:** Perform advanced analysis on the collected data using RAG capabilities.
   - [x] 😊 **User-Friendly Interface:** Experience an intuitive interface designed for ease of use and efficiency.
   - [x] 🖥️ **OS Interaction:** Execute code directly from the prompt, providing real-time, relevant, and actionable intelligence.

## 3. Installation:

1. Clone repo
   ``` bash
      git clone https://github.com/noualibechir/rag_osint.git #change to the right one
      cd rag_osint
   
   ```
2. Create a new environment 
    ``` bash
       python -m venv .env
    
    ```
3. Activate the new environment

   **Linux**

    ```bash
       source .env/bin/activate
    
    ```
4. Install dependencies 
   
   ```bash
      sudo apt update
   
      #install docker
      sudo apt install -y docker.io
      sudo systemctl enable docker --now
      sudo usermod -aG docker $USER
   
      #install ollama for embedding
      curl -fsSL https://ollama.com/install.sh | sh
   
      #install sherlock
      sudo apt install sherlock
   
      #install dependencies
      pip install -r requirements.txt
    
   ```
   Or

   ```bash
      chmod +x install.sh
      ./install.sh
   
   ```
5. Add envirement variable:

   ```bash
      export GROQ_API_KEY=***your_key***
      export OPENAI_API_KEY=***your_key***

   ```

6. Run pgvector:

   ```bash
      ollama run nomic-embed-text
      chmod +x run_pgvector.sh
      ./run_pgvector.sh
   ```
7. Run:

   ```bash
      streamlit run app.py --server.address==localhost 
   ```
## 4. Tutorial:
 This tutorial will guide you through the process of gathering information and creating a list of potential passwords for brute force attacks using the RAG OSINT tool as an example.

 1. **Step 1: Web Research with RAG** 🌐🔍
   - Gather profiles(social media), articles and mentions of the target from various online sources.
   - Finding URLs/Documents related to the target.

2. **Step 2: Adding Knowledge to LLM** 📚 
   - Input the collected data into the tool to augment its knowledge base.

3. **Step 3: Creating Potential Passwords for Brute Force Attacks** 🔓
   - Use the tool to create combinations and permutations of the gathered information.
   - Generate a list of potential passwords that can be used for security testing and vulnerability assessment.
![video](assets/video_tuto.mp4)


## 5. Acknowledgements 🙏 :

 We extend our deepest gratitude to the following organizations for their invaluable contributions and support in the development of this project:

   - **[Ollama](https://ollama.com/)**: For their cutting-edge solutions and support that have significantly contributed to the success of this project.
   - **[Groq](https://groq.com/)**: For their innovative hardware solutions that enhance our computational capabilities and efficiency.
   - **[Phidata](https://www.phidata.com/)**: For their exceptional data management and analytics solutions that help in refining and optimizing our processes.
   - **[Streamlit](https://streamlit.io/)**: For their fantastic framework that allows us to create interactive and user-friendly applications with ease.

 Your support and resources have been instrumental in bringing this project to life. Thank you!

 ## Special thanks for the target role: Chuck Keith (Networkchuck) 
