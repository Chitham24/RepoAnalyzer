# RepoAnalyzer

RepoAnalyzer is a modular tool that analyzes public GitHub repositories
and generates structured, easy‑to‑read reports with architecture
summaries, dependency insights, and visual diagrams.

------------------------------------------------------------------------

## Overview

Given a GitHub repository URL, RepoAnalyzer:

-   Loads repository metadata and source files from GitHub
-   Performs static analysis of code and structure
-   Uses LLMs to generate concise summaries
-   Builds dependency and execution‑flow graphs
-   Produces clean reports in Markdown and JSON formats
-   Generates Mermaid diagrams for visualization

------------------------------------------------------------------------

## Features

### End‑to‑End Analysis Pipeline

Ingestion → Static Analysis → LLM Summarization → Graph Generation →
Final Report

### Structured Outputs

-   `report.md` --- Human‑readable GitHub‑friendly report
-   `report.json` --- Machine‑readable structured output

### Mermaid Diagrams

-   Dependency graph
-   Execution flow
-   Module structure

Diagrams are saved as `.mmd` files.

### Flexible LLM Support

Selectable provider from the UI: - OpenAI - Groq - Gemini

Model configuration is controlled via environment variables.

### Clean Architecture

-   **Analysis logic** separated from UI
-   **Report building** independent from formatting
-   **UI layer** contains orchestration only

------------------------------------------------------------------------

## Tech Stack

-   **Language:** Python
-   **UI:** Streamlit
-   **Diagrams:** Mermaid
-   **Integrations:** GitHub REST API
-   **LLM Providers:** OpenAI, Groq, Gemini

------------------------------------------------------------------------

## Output Structure

After running an analysis:

    outputs/
    └── <repo_name>/
        ├── report.md
        ├── report.json
        ├── diagrams/
        │   ├── dependency.mmd
        │   └── execution_flow.mmd
        └── metadata.json

------------------------------------------------------------------------

## Project Structure

    github_client/   GitHub API client and repository loading
    analysis/        Static analysis modules
    llm/             File, folder, and repo summarization
    graph/           Dependency and execution‑flow graph builders
    output/
      ├── report_builder.py   Structured report assembly
      └── formatter.py        Markdown and JSON formatting
    ui/
      └── app.py              Streamlit UI and orchestration

------------------------------------------------------------------------

## Running the Project

### 1. Install Dependencies

Install required packages.

### 2. Configure Environment Variables

Add API keys and configuration values in a `.env` file.

### 3. Start the UI

``` bash
streamlit run ui/app.py
```

Then:

1.  Paste a public GitHub repository URL
2.  Select an LLM provider
3.  Click **Analyze Repository**

You can view: - Rendered Markdown report - Mermaid diagrams - JSON
output - Saved artifacts under `outputs/<repo_name>/`

------------------------------------------------------------------------

## Configuration

### Required

-   `GITHUB_TOKEN` (recommended to avoid rate limits)

### Provider API Keys

-   `OPENAI_API_KEY`
-   `GROQ_API_KEY`
-   `GEMINI_API_KEY`

### LLM Settings

-   `LLM_PROVIDER`
-   `LLM_MODEL_NAME`
-   `LLM_MAX_TOKENS`
-   `LLM_TEMPERATURE`

### Tips for Concise Outputs

-   Reduce `LLM_MAX_TOKENS`
-   Lower `LLM_TEMPERATURE`

------------------------------------------------------------------------

## Limitations

-   Summary quality depends on model and prompts
-   Large repositories may require file limits for performance and
    readability
-   GitHub API rate limits may apply without authentication

------------------------------------------------------------------------
