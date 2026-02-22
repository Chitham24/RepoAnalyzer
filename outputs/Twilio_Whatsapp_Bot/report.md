# Twilio_Whatsapp_Bot Analysis Report

**Owner:** Chitham24  
**Repository:** Twilio_Whatsapp_Bot  
**Branch:** main  
**Primary Language:** Python  

**Description:** This project is a Flask-based automation tool that uses Twilio's WhatsApp API to send personalized messages, track user responses, and send follow-up reminders if users don’t respond within 24 hours.

## 📋 Overview

**Architecture Pattern:** Modular application


## 🛠️ Technology Stack

### Languages

| Language | Files | Lines | Percentage |
|----------|-------|-------|------------|
| Python | 6 | 217 | 85.7% |
| Markdown | 1 | 63 | 14.3% |

### Frameworks
- Flask

### Databases
- Redis


## 🏗️ Architecture Insights


## 📁 Repository Structure

**Total Folders:** 0


## 🚀 Entry Points

**Total Entry Points:** 2

### Application Files
- `main.py` (Python)

### Framework Entry Points
- `server.py` (Framework: Flask)


## 🔄 Execution Flow




## 📊 Visual Diagrams

### Execution Flow Diagram

```mermaid
graph LR
    entry["Application entry points"]
    database["Data persistence layer"]
    external["External services and infrastructure"]
    entry -->|Data operations| database

    style entry fill:#e1f5e1,stroke:#4caf50,stroke-width:3px
    style database fill:#fce4ec,stroke:#e91e63,stroke-width:2px
    style external fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
```

### Module Structure Diagram

```mermaid
graph TD
    Empty[No modules detected]
```

### Dependency Graph

```mermaid
graph TD
    README_md[README.md]
    llm_py[llm.py]
    logger_py[logger.py]
    main_py[main.py]
    message_log_txt[message_log.txt]
    requirements_txt[requirements.txt]
    server_py[server.py]
    tracker_py[tracker.py]
    utils_py[utils.py]
    main_py --> utils_py
    server_py --> logger_py
    server_py --> tracker_py
    tracker_py --> logger_py
    utils_py --> llm_py
    utils_py --> tracker_py

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:2px
```


## 🔗 Dependencies

**Total Nodes:** 9  
**Total Edges:** 6  
