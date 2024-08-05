from typing import List
import nest_asyncio
import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from phi.utils.log import logger
from assistant import get_llm_os  # type: ignore
from utils import restart_assistant, get_image
from PIL import Image
from config import config

#----------------Intialization------- 

logo=get_image(config["logo_path"],128,128)
st.logo(logo,icon_image=logo)

nest_asyncio.apply()
st.set_page_config(
    page_title="Rag Osint",
    page_icon=logo,
)

#-----------------Welcome page---------------------------

@st.experimental_dialog("Welcome To Rag Osint",width="large")
def welcome():
    st.title("Special thanks for:")
    col1,col2,col3 = st.columns(3)
    with col1:
        #ollama_logo = get_image(config["ollama_logo_path"],512,512)
        st.image(config["ollama_logo_path"],use_column_width=True)
        st.link_button("Ollama", "https://ollama.com/",use_container_width=True)
    with col2:
        #groq_logo = get_image(config["groq_logo_path"],512,512)
        st.image(config["groq_logo_path"],use_column_width=True) 
        st.link_button("Groq", "https://groq.com/",use_container_width=True)
        run=st.button("To app",type="primary",use_container_width=True)
            
    with col3:
        #phidata_logo = get_image(config["phidata_logo_path"],512,512)
        st.image(config["phidata_logo_path"],use_column_width=True)
        st.link_button("Phidata", "https://www.phidata.com/",use_container_width=True)
    
    if run: 
        st.session_state.welcome = True
        st.rerun()


#------------------build main section--------------

def main() -> None:
    # Get LLM Model
    llm_id = st.sidebar.selectbox("Select LLM", options=config["llm_names"])
    # Set llm_id in session state
    if "llm_id" not in st.session_state:
        st.session_state["llm_id"] = llm_id
    # Restart the assistant if llm_id changes
    elif st.session_state["llm_id"] != llm_id:
        st.session_state["llm_id"] = llm_id
        restart_assistant()
    # Get embedder
    embedding_models = st.sidebar.selectbox("Select Embedder", options=config["embedding_models"])
    # Set llm_id in session state
    if "embedding_models" not in st.session_state:
        st.session_state["embedding_models"] = embedding_models
    # Restart the assistant if llm_id changes
    elif st.session_state["embedding_models"] != embedding_models:
        st.session_state["embedding_models"] = embedding_models
        restart_assistant()

    # Sidebar checkboxes for selecting tools
    st.sidebar.markdown("### Select Tools")


    # Enable file tools
    if "file_tools_enabled" not in st.session_state:
        st.session_state["file_tools_enabled"] = True
    # Get file_tools_enabled from session state if set
    file_tools_enabled = st.session_state["file_tools_enabled"]
    # Checkbox for enabling shell tools
    file_tools = st.sidebar.toggle("File Tools", value=file_tools_enabled, help="Enable file tools.")
    if file_tools_enabled != file_tools:
        st.session_state["file_tools_enabled"] = file_tools
        file_tools_enabled = file_tools
        restart_assistant()

    # Enable Web Search via DuckDuckGo
    if "ddg_search_enabled" not in st.session_state:
        st.session_state["ddg_search_enabled"] = True
    # Get ddg_search_enabled from session state if set
    ddg_search_enabled = st.session_state["ddg_search_enabled"]
    # Checkbox for enabling web search
    ddg_search = st.sidebar.toggle("Web Search", value=ddg_search_enabled, help="Enable web search using DuckDuckGo.")
    if ddg_search_enabled != ddg_search:
        st.session_state["ddg_search_enabled"] = ddg_search
        ddg_search_enabled = ddg_search
        restart_assistant()

    # Enable shell tools
    if "shell_tools_enabled" not in st.session_state:
        st.session_state["shell_tools_enabled"] = True
    # Get shell_tools_enabled from session state if set
    shell_tools_enabled = st.session_state["shell_tools_enabled"]
    # Checkbox for enabling shell tools
    shell_tools = st.sidebar.toggle("Shell Tools", value=shell_tools_enabled, help="Enable shell tools.")
    if shell_tools_enabled != shell_tools:
        st.session_state["shell_tools_enabled"] = shell_tools
        shell_tools_enabled = shell_tools
        restart_assistant()

    # Sidebar checkboxes for selecting team members
    st.sidebar.markdown("### Select Team Members")


    # Enable Python Assistant
    if "python_assistant_enabled" not in st.session_state:
        st.session_state["python_assistant_enabled"] = False
    # Get python_assistant_enabled from session state if set
    python_assistant_enabled = st.session_state["python_assistant_enabled"]
    # Checkbox for enabling web search
    python_assistant = st.sidebar.toggle(
        "Python Assistant",
        value=python_assistant_enabled,
        help="Enable the Python Assistant for writing and running python code.",
    )
    if python_assistant_enabled != python_assistant:
        st.session_state["python_assistant_enabled"] = python_assistant
        python_assistant_enabled = python_assistant
        restart_assistant()

    # Get the assistant
    llm_os: Assistant
    if "llm_os" not in st.session_state or st.session_state["llm_os"] is None:
        logger.info(f"---*--- Creating {llm_id} LLM OS ---*---")
        llm_os = get_llm_os(
            llm_id=llm_id,
            ddg_search=ddg_search_enabled,
            file_tools=file_tools_enabled,
            shell_tools=shell_tools_enabled,
            python_assistant=python_assistant_enabled,
        )
        st.session_state["llm_os"] = llm_os
    else:
        llm_os = st.session_state["llm_os"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    try:
        st.session_state["llm_os_run_id"] = llm_os.create_run()
    except Exception:
        st.warning("Could not create LLM OS run, is the database running?")
        return

    # Load existing messages
    assistant_chat_history = llm_os.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me questions..."}]

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display existing chat messages
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is from a user, generate a new response
    last_message = st.session_state["messages"][-1]
    if last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            response = ""
            resp_container = st.empty()
            for delta in llm_os.run(question):
                response += delta  # type: ignore
                resp_container.markdown(response)
            st.session_state["messages"].append({"role": "assistant", "content": response})

    # Load LLM OS knowledge base
    if llm_os.knowledge_base:
        # -*- Add websites to knowledge base
        if "url_scrape_key" not in st.session_state:
            st.session_state["url_scrape_key"] = 0

        input_url = st.sidebar.text_input(
            "Add URL to Knowledge Base", type="default", key=st.session_state["url_scrape_key"]
        )
        add_url_button = st.sidebar.button("Add URL")
        if add_url_button:
            if input_url is not None:
                alert = st.sidebar.info("Processing URLs...", icon="👁️")
                if f"{input_url}_scraped" not in st.session_state:
                    scraper = WebsiteReader(max_links=2, max_depth=1)
                    web_documents: List[Document] = scraper.read(input_url)
                    if web_documents:
                        llm_os.knowledge_base.load_documents(web_documents, upsert=True)
                    else:
                        st.sidebar.error("Could not read website")
                    st.session_state[f"{input_url}_uploaded"] = True
                alert.empty()

        # Add PDFs to knowledge base
        if "file_uploader_key" not in st.session_state:
            st.session_state["file_uploader_key"] = 100

        uploaded_file = st.sidebar.file_uploader(
            "Add a PDF :page_facing_up:", type="pdf", key=st.session_state["file_uploader_key"]
        )
        if uploaded_file is not None:
            alert = st.sidebar.info("Processing PDF...", icon="👁️")
            auto_rag_name = uploaded_file.name.split(".")[0]
            if f"{auto_rag_name}_uploaded" not in st.session_state:
                reader = PDFReader()
                auto_rag_documents: List[Document] = reader.read(uploaded_file)
                if auto_rag_documents:
                    llm_os.knowledge_base.load_documents(auto_rag_documents, upsert=True)
                else:
                    st.sidebar.error("Could not read PDF")
                st.session_state[f"{auto_rag_name}_uploaded"] = True
            alert.empty()

    if llm_os.knowledge_base and llm_os.knowledge_base.vector_db:
        if st.sidebar.button("Clear Knowledge Base"):
            llm_os.knowledge_base.vector_db.clear()
            st.sidebar.success("Knowledge base cleared")

    # Show team member memory
    if llm_os.team and len(llm_os.team) > 0:
        for team_member in llm_os.team:
            if len(team_member.memory.chat_history) > 0:
                with st.status(f"{team_member.name} Memory", expanded=False, state="complete"):
                    with st.container():
                        _team_member_memory_container = st.empty()
                        _team_member_memory_container.json(team_member.memory.get_llm_messages())

    if llm_os.storage:
        llm_os_run_ids: List[str] = llm_os.storage.get_all_run_ids()
        new_llm_os_run_id = st.sidebar.selectbox("Run ID", options=llm_os_run_ids)
        if st.session_state["llm_os_run_id"] != new_llm_os_run_id:
            logger.info(f"---*--- Loading {llm_id} run: {new_llm_os_run_id} ---*---")
            st.session_state["llm_os"] = get_llm_os(
                llm_id=llm_id,
                ddg_search=ddg_search_enabled,
                file_tools=file_tools_enabled,
                shell_tools=shell_tools_enabled,
                python_assistant=python_assistant_enabled,
                run_id=new_llm_os_run_id,
            )
            st.rerun()

    if st.sidebar.button("New Run"):
        restart_assistant()

if __name__=="__main__":

    if "welcome" not in st.session_state:
        welcome()
    else:
        main()