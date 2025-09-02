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
