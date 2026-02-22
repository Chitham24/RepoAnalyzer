import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import uuid

import streamlit.components.v1 as components

import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import all necessary modules
from github_client.repo_loader import RepoLoader
from analysis.language_detector import get_repo_language_stats  # Changed from detect_languages
from analysis.stack_detector import detect_frameworks, detect_databases, detect_infrastructure  # Import individual functions
from analysis.structure_analyzer import classify_folders  # This is correct
from analysis.entrypoint_finder import find_entrypoints  # Changed from detect_entrypoints

# LLM layer - These are correct (classes)
from llm.file_summarizer import FileSummarizer
from llm.folder_summarizer import FolderSummarizer
from llm.repo_summarizer import RepoSummarizer

# Graph layer - These are correct (functions)
from graph.dependency_graph import build_dependency_graph
from graph.flow_builder import build_execution_flow
from graph.diagram_generator import (
    generate_dependency_diagram,
    generate_flow_diagram,
    generate_module_diagram,
)

# Output layer - These are correct
from output.report_builder import build_report
from output.formatter import format_markdown, format_json

load_dotenv()
# DEBUG
github_token = os.getenv("GITHUB_TOKEN")
if github_token:
    st.sidebar.success(f"✅ GitHub token loaded (ends with: ...{github_token[-4:]})")
else:
    st.sidebar.error("❌ GITHUB_TOKEN not found in .env file!")
# DEBUG ENDS
def save_outputs(repo_name: str, markdown_report: str, json_report: str, diagrams: dict):
    """
    Save all generated outputs to disk.
    
    Args:
        repo_name: Repository name for folder creation
        markdown_report: Markdown report content
        json_report: JSON report content
        diagrams: Dictionary with diagram content
    """
    # Create output directory structure
    output_dir = Path("outputs") / repo_name
    diagrams_dir = output_dir / "diagrams"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    diagrams_dir.mkdir(exist_ok=True)
    
    # Save markdown report
    with open(output_dir / "report.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    
    # Save JSON report
    with open(output_dir / "report.json", "w", encoding="utf-8") as f:
        f.write(json_report)
    
    # Save diagrams
    if diagrams.get("dependency_diagram"):
        with open(diagrams_dir / "dependency.mmd", "w", encoding="utf-8") as f:
            f.write(diagrams["dependency_diagram"])
    
    if diagrams.get("flow_diagram"):
        with open(diagrams_dir / "execution_flow.mmd", "w", encoding="utf-8") as f:
            f.write(diagrams["flow_diagram"])
    
    if diagrams.get("module_diagram"):
        with open(diagrams_dir / "module_structure.mmd", "w", encoding="utf-8") as f:
            f.write(diagrams["module_diagram"])
    
    # Save metadata
    metadata = {
        "repo_name": repo_name,
        "analysis_date": datetime.now().isoformat(),
        "output_location": str(output_dir.absolute()),
    }
    
    import json
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    return str(output_dir.absolute())


def parse_github_url(url: str) -> tuple:
    """
    Parse GitHub URL to extract owner and repo.
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Tuple of (owner, repo) or (None, None) if invalid
    """
    url = url.strip().rstrip("/")
    
    # Handle different URL formats
    if "github.com" in url:
        parts = url.split("github.com/")[-1].split("/")
        if len(parts) >= 2:
            return parts[0], parts[1]
    
    return None, None

def render_mermaid(mermaid_code: str, height: int = 500):
    diagram_id = f"mermaid-{uuid.uuid4()}"

    html = f"""
    <div id="{diagram_id}" class="mermaid">
    {mermaid_code}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{
            startOnLoad: false,
            theme: "default"
        }});

        const el = document.getElementById("{diagram_id}");
        if (el) {{
            mermaid.run({{ nodes: [el] }});
        }}
    </script>
    """

    components.html(html, height=height)


def run_analysis(owner: str, repo: str, branch: str, llm_provider: str):
    """
    Run the complete analysis pipeline.
    
    Args:
        owner: GitHub repository owner
        repo: Repository name
        branch: Branch name
        llm_provider: LLM provider to use
        
    Returns:
        Tuple of (report_dict, markdown_report, json_report, output_path)
    """
    # Set LLM provider in environment
    os.environ["LLM_PROVIDER"] = llm_provider
    
    # Stage 1: Load repository
    st.write("📥 **Stage 1: Loading repository...**")
    progress_bar = st.progress(0)
    
    repo_url = f"https://github.com/{owner}/{repo}"
    repo_loader = RepoLoader()
    repo_data = repo_loader.load_repository(repo_url, branch)
    # Debug
    # st.write("**DEBUG: repo_data keys:**", list(repo_data.keys()))
    # st.write("**DEBUG: repo_data structure:**", repo_data)
    # Debug ends
    files = repo_data["files"]
    metadata = repo_data["metadata"]
    progress_bar.progress(15)
    st.success(f"✅ Loaded {len(files)} files from {owner}/{repo}")
    
    # Stage 2: Static Analysis
    st.write("🔍 **Stage 2: Running static analysis...**")
    
    # Language detection
    st.write("   - Detecting languages...")
    language_stats = get_repo_language_stats(files)
    progress_bar.progress(25)
    
    # Stack detection
    st.write("   - Detecting tech stack...")
    frameworks = detect_frameworks(files)
    databases = detect_databases(files)
    infrastructure = detect_infrastructure(files)
    progress_bar.progress(35)
    
    # Structure analysis
    st.write("   - Analyzing folder structure...")
    folder_structure = classify_folders(files)
    progress_bar.progress(45)
    
    # Entry point detection
    st.write("   - Detecting entry points...")
    entrypoints = find_entrypoints(files)
    progress_bar.progress(50)
    
    st.success("✅ Static analysis complete")
    
    # Stage 3: LLM Summaries
    st.write("🤖 **Stage 3: Generating LLM summaries...**")
    
    # File summaries (limit to important files)
    st.write("   - Summarizing key files...")
    file_summarizer = FileSummarizer()
    file_summaries = []
    
    # Prioritize entry points and important files
    important_files = [e["path"] for e in entrypoints.get("application_files", [])][:10]
    for file_obj in files:
        if file_obj["path"] in important_files:
            summary = file_summarizer.summarize_file(file_obj["path"], file_obj["content"])
            file_summaries.append(summary)
    progress_bar.progress(60)
    
    # Folder summaries
    st.write("   - Summarizing modules...")
    folder_summarizer = FolderSummarizer()
    folder_summaries = []
    
    for folder_path, folder_info in folder_structure.items():
        # Get files in this folder
        folder_files = [s for s in file_summaries if s["path"].startswith(folder_path)]
        if folder_files:
            summary = folder_summarizer.summarize_folder(
                folder_path,
                folder_info["role"],
                folder_files
            )
            folder_summaries.append(summary)
    progress_bar.progress(70)
    
    # Repository summary
    st.write("   - Generating repository overview...")
    repo_summarizer = RepoSummarizer()
    
    architecture_summary = repo_summarizer.summarize_architecture(
        repo_name=repo,
        description=metadata.get("description", ""),
        languages=language_stats["languages"],
        frameworks=frameworks,
        databases=databases,
        infrastructure=infrastructure,
        folder_summaries=folder_summaries,
        entrypoints=entrypoints
    )
    
    execution_flow_summary = repo_summarizer.summarize_execution_flow(
        repo_name=repo,
        entrypoints=entrypoints,
        frameworks=frameworks,
        folder_summaries=folder_summaries
    )
    progress_bar.progress(80)
    
    st.success("✅ LLM summaries generated")
    
    # Stage 4: Graph & Flow Building
    st.write("📊 **Stage 4: Building graphs and flows...**")
    
    # Dependency graph
    st.write("   - Building dependency graph...")
    dependency_graph = build_dependency_graph(files)
    progress_bar.progress(85)
    
    # Execution flow
    st.write("   - Building execution flow...")
    execution_flow = build_execution_flow(
        entrypoints=entrypoints,
        folder_summaries=folder_summaries,
        frameworks=frameworks,
        databases=databases,
        infrastructure=infrastructure
    )
    progress_bar.progress(90)
    
    # Generate diagrams
    st.write("   - Generating Mermaid diagrams...")
    dependency_diagram = generate_dependency_diagram(dependency_graph, max_nodes=15)
    flow_diagram = generate_flow_diagram(execution_flow)
    module_diagram = generate_module_diagram(folder_summaries, max_modules=10)
    progress_bar.progress(95)
    
    st.success("✅ Graphs and flows built")
    
    # Stage 5: Build Final Report
    st.write("📝 **Stage 5: Building final report...**")
    
    report = build_report(
        repo_metadata=metadata,
        language_stats=language_stats,
        frameworks=frameworks,
        databases=databases,
        infrastructure=infrastructure,
        folder_structure=folder_structure,
        entrypoints=entrypoints,
        file_summaries=file_summaries,
        folder_summaries=folder_summaries,
        architecture_summary=architecture_summary,
        execution_flow_summary=execution_flow_summary,
        dependency_graph_dict=dependency_graph.to_dict(),
        execution_flow_dict=execution_flow.to_dict(),
        dependency_diagram=dependency_diagram,
        flow_diagram=flow_diagram,
        module_diagram=module_diagram
    )
    
    # Format reports
    markdown_report = format_markdown(report)
    json_report = format_json(report)
    progress_bar.progress(98)
    
    # Save outputs
    st.write("💾 **Saving outputs to disk...**")
    output_path = save_outputs(
        repo_name=repo,
        markdown_report=markdown_report,
        json_report=json_report,
        diagrams=report["diagrams"]
    )
    progress_bar.progress(100)
    
    st.success(f"✅ Analysis complete! Outputs saved to: `{output_path}`")
    
    return report, markdown_report, json_report, output_path


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="RepoAnalyzer",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 RepoAnalyzer")
    st.markdown("**Automated GitHub Repository Analysis with AI-Powered Insights**")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # LLM Provider selection
        llm_provider = st.selectbox(
            "Select LLM Provider",
            options=["openai", "gemini", "groq"],
            index=0,
            help="Choose the LLM provider for code analysis"
        )
        
        st.markdown("---")
        st.markdown("### 📝 Instructions")
        st.markdown("""
        1. Enter a public GitHub repository URL
        2. Select your preferred LLM provider
        3. Click 'Analyze Repository'
        4. Wait for the analysis to complete
        5. View results and download reports
        """)
        
        st.markdown("---")
        st.markdown("### 🔑 API Keys")
        st.markdown("""
        Make sure your `.env` file contains:
        - `GITHUB_TOKEN`
        - `OPENAI_API_KEY` (if using OpenAI)
        - `GEMINI_API_KEY` (if using Gemini)
        - `GROQ_API_KEY` (if using Groq)
        """)
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/owner/repository",
            help="Enter the full URL of a public GitHub repository"
        )
    
    with col2:
        branch = st.text_input(
            "Branch",
            value="main",
            help="Branch to analyze"
        )
    
    analyze_button = st.button("🚀 Analyze Repository", type="primary", use_container_width=True)
    
    if analyze_button:
        if not repo_url:
            st.error("❌ Please enter a GitHub repository URL")
            return
        
        # Parse GitHub URL
        owner, repo = parse_github_url(repo_url)

        # DEBUG
        st.write(f"**Debug Info:**")
        st.write(f"- Owner: `{owner}`")
        st.write(f"- Repo: `{repo}`")
        st.write(f"- Branch: `{branch}`")
        st.write(f"- Full URL: `https://github.com/{owner}/{repo}`")
        # DEBUG ENDS
        if not owner or not repo:
            st.error("❌ Invalid GitHub URL. Please use format: https://github.com/owner/repository")
            return
        
        st.info(f"📊 Analyzing: **{owner}/{repo}** (branch: {branch})")
        
        try:
            # Run analysis
            report, markdown_report, json_report, output_path = run_analysis(
                owner=owner,
                repo=repo,
                branch=branch,
                llm_provider=llm_provider
            )
            
            st.markdown("---")
            st.success("🎉 **Analysis Complete!**")
            
            # Display results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Report", "📊 Diagrams", "📦 JSON", "💾 Downloads"])
            
            with tab1:
                st.markdown("### Repository Analysis Report")
                st.markdown(markdown_report)
            
            with tab2:
                st.markdown("### Visual Diagrams")

                diagrams = report.get("diagrams", {})

                if diagrams.get("flow_diagram"):
                    st.markdown("#### Execution Flow Diagram")
                    render_mermaid(diagrams["flow_diagram"], height=450)

                if diagrams.get("module_diagram"):
                    st.markdown("#### Module Structure Diagram")
                    render_mermaid(diagrams["module_diagram"], height=450)

                if diagrams.get("dependency_diagram"):
                    st.markdown("#### Dependency Graph")
                    render_mermaid(diagrams["dependency_diagram"], height=600)

            with tab3:
                st.markdown("### JSON Report")
                st.json(report)
            
            with tab4:
                st.markdown("### Download Reports")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button(
                        label="📄 Download Markdown",
                        data=markdown_report,
                        file_name=f"{repo}_analysis.md",
                        mime="text/markdown"
                    )
                
                with col2:
                    st.download_button(
                        label="📦 Download JSON",
                        data=json_report,
                        file_name=f"{repo}_analysis.json",
                        mime="application/json"
                    )
                
                with col3:
                    st.markdown(f"**Files saved to:**\\n`{output_path}`")
        
        except Exception as e:
            st.error(f"❌ **Analysis failed:** {str(e)}")
            st.exception(e)


if __name__ == "__main__":
    main()