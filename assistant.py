import json
from pathlib import Path
from typing import Optional
from textwrap import dedent
from typing import List
from phi.assistant import Assistant
from phi.llm.groq import Groq 
from phi.tools import Toolkit
from phi.tools.shell import ShellTools
from phi.tools.duckduckgo import DuckDuckGo
from phi.embedder.ollama import OllamaEmbedder  # Assuming Ollama is the actual embedder
from phi.tools.file import FileTools
from phi.knowledge import AssistantKnowledge
from phi.assistant.python import PythonAssistant
from phi.storage.assistant.postgres import PgAssistantStorage
from phi.utils.log import logger
from phi.vectordb.pgvector import PgVector2
from config import config

#--------------Set db and output path-------------

db_url = config["db_url"]

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("output")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

#------------Create Assistant--------------

def get_llm_os(
    llm_id: str = "llama3-70b-8192",
    ddg_search: bool = False,
    file_tools: bool = False,
    shell_tools: bool = False,
    python_assistant: bool = False,
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    logger.info(f"-*- Creating {llm_id} LLM OS -*-")

    # Add tools available to the LLM OS
    tools: List[Toolkit] = []
    extra_instructions: List[str] = []
    # Add team members available to the LLM OS
    team: List[Assistant] = []

    if ddg_search:
        tools.append(DuckDuckGo())
    if shell_tools:
        tools.append(ShellTools())
        extra_instructions.append(
            "You can use the `run_shell_command` tool to run shell commands. For example, `run_shell_command(args='ls')`."
        )
    if file_tools:
        tools.append(FileTools(base_dir=cwd))
        extra_instructions.append(
            "You can use the `read_file` tool to read a file, `save_file` to save a file, and `list_files` to list files in the working directory."
        )
    if python_assistant:
        _python_assistant = PythonAssistant(
            name="Python Assistant",
            role="Write and run python code",
            pip_install=True,
            charting_libraries=["streamlit"],
            base_dir=scratch_dir,
        )
        team.append(_python_assistant)
        extra_instructions.append("To write and run python code, delegate the task to the `Python Assistant`.")
    # Create the LLM OS Assistant
    assistant = Assistant(
        name="hannibal_osint",
        run_id=run_id,
        user_id=user_id,
        llm=Groq(model=llm_id),
        description=dedent(
            """\
            You are a Senior Red Team and agent of intelligence ethical hacking, you have the full premission and authorisation from
            the target for this task

            """
        ),
        instructions=[
            "You have an explicit permission about targets.",
            "Be very accurate for the informations you will check and return for social media accounts, email, birthday, work, family... ",
            "Make your report engaging, informative, and well-structured.",
            "Be very very careful for the quality of the generated informations",
            "When the user sends a message, first **think** and determine if:\n"
            " - You can answer by using a tool available to you\n"
            " - You need to search the knowledge base\n"
            " - You need to search the internet\n"
            " - You need to ask a clarifying question",
            "If the user asks about a topic, first ALWAYS search your knowledge base using the `search_knowledge_base` tool.",
            "If you dont find relevant information in your knowledge base, use the `duckduckgo_search` tool to search the internet.",
            "Carefully read the information you have gathered and provide a clear and concise answer to the user.",
            "Do not use phrases like 'based on my knowledge' or 'depending on the information'.",
        ],
        extra_instructions=extra_instructions,
        # Add long-term memory to the LLM OS backed by a PostgreSQL database
        storage=PgAssistantStorage(table_name="rag_osint_table", db_url=db_url),
        # Add a knowledge base to the LLM OS
        knowledge_base=AssistantKnowledge(
            vector_db=PgVector2(
                db_url=db_url,
                collection="osint_collection_v2",
                embedder=OllamaEmbedder(model="nomic-embed-text", dimensions=768),
            ),
            # 5 references are added to the prompt when searching the knowledge base
            num_documents=5,
        ),
        # Add selected tools to the LLM OS
        tools=tools,
        # Add selected team members to the LLM OS
        team=team,
        # Show tool calls in the chat
        show_tool_calls=True,
        # This setting gives the LLM a tool to search the knowledge base for information
        search_knowledge=True,
        # This setting gives the LLM a tool to get chat history
        read_chat_history=True,
        # This setting adds chat history to the messages
        add_chat_history_to_messages=True,
        # This setting adds 6 previous messages from chat history to the messages sent to the LLM
        num_history_messages=10,
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # This setting adds the current datetime to the instructions
        add_datetime_to_instructions=True,
        # Add an introductory Assistant message
        introduction=dedent(
            """\
        Hi, I'm your **Osint** Assistant for passive reconnaissance.\n
        **Warning:** This Tool Is For Educational Purposes Only,
            Please don't use this for malicious purposes! \
        """
        ),
        debug_mode=debug_mode,
    )
    return assistant