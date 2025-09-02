# PyMac

A Python Interface API for **UI Automation** and **AI Agents**.

## Overview

**PyMac** was developed to enable seamless **data extraction**, **automation**, and the creation of **autonomous AI agents** capable of interacting with macOS via the Accessibility APIs. This package simplifies integration with macOS Accessibility, making it accessible from Python. Additionally, PyMac includes tools for data cleaning and processing to improve quality for large language models (LLMs) and integrates with [LangChain](https://github.com/langchain-ai/langchain) to build AI Agents that can interact with user interfaces.

A key feature of PyMac is its use of the **text-based accessibility tree**, which allows interaction with the UI without relying on vision-language models (VLMs). By leveraging the same accessibility tools used by individuals with disabilities, PyMac enables AI agents to interact with the UI independently of VLMs, providing a flexible and universal solution for autonomous agent development.

## Features

- **UI Interaction**: Access and manipulate UI elements programmatically.  
- **Data Processing**: Clean and process data to optimize for LLM integrations.  
- **LangChain Integration**: Build AI Agents capable of interacting with applications using LangChain tools and examples.  

## Installation

```bash
pip install pymac
Getting Started
Prerequisites
Python 3.11+ installed on your system.
```
Accessibility permissions enabled for your Python interpreter.

Enabling Accessibility Permissions
Open System Preferences > Security & Privacy > Privacy tab.

Select Accessibility from the left panel.

Click the lock icon to make changes and enter your password.

Click the + button and add your Python interpreter (e.g., /usr/local/bin/python3).

Important Disclaimer
Full System Access: PyMac grants access to system applications and data, including minimized or backgrounded apps. Exercise caution to avoid exposing sensitive information or performing unintended actions.

Data Privacy: Avoid sending personal or sensitive information to external services or APIs.

Require User Confirmation: AI agents or automation scripts will not execute actions without explicit user confirmation.

Examples
To get started, clone the repository and set up the environment:

bash
Copy code
```
git clone git@github.com:Aashi-ghub/pymac.git
cd pymac
poetry install
```
Interactive Jupyter Notebook
PyMac provides an interactive Jupyter notebook demonstrating basic usage. To run it:

bash
Copy code
```
cd examples
poetry run jupyter lab
```
AI Agent Web UI Example
The repository includes LangChain tool integration and an AI Agent capable of interacting with UI elements.

To launch the AI Agent using the Chainlit web UI:

bash
Copy code
cd examples
chainlit run pymac_agent.py -w
Open the web UI in your browser: http://localhost:8000.

Select the application to interact with from the settings dropdown.

Interact with the AI Agent through the input field. The agent reads UI state, sets properties, and can perform actions, but only after explicit user confirmation.

Basic Usage
Accessing Applications
Accessing Running Applications
python
Copy code
from pymac.application import get_running_applications

apps = get_running_applications()
for app in apps:
    print(app.localized_name, app.pid)
Interacting with the Frontmost Application
python
Copy code
from pymac.application import Application

app = Application.from_frontmost_app()
print(f"Interacting with: {app.localized_name}")

app.refresh_ui_tree()
root_element = app.root_ui_element
Working with UI Elements
Exploring UI Elements
python
Copy code
ui_tree = root_element.asdict()
print(ui_tree)
Accessing Specific UI Elements
python
Copy code
element_id = 'AXButton__OK__123456789'
ui_element = app.get_ui_element(element_id)

print(ui_element.attributes)
print(ui_element.AXTitle)
print(ui_element.AXRole)
Performing Actions on UI Elements
python
Copy code
print(ui_element.actions)

try:
    ui_element.AXPress()
    print("Action performed successfully.")
except UIActionError as e:
    print(f"Failed to perform action: {e}")
Contributing
Contributions are welcome. You can help by reporting issues, adding features, improving documentation, or suggesting ideas.
