.. Py2Mac documentation master file

Welcome to Py2Mac's Documentation!
===================================

Overview
--------

**Py2Mac**: A Python Interface to macOS Accessibility API for **UI Automation** and **AI Agents**



Installation
------------

Install Py2Mac via pip:

.. code-block:: bash

   pip install py2mac

Requirements:

- Python 3.11+
- macOS system with Accessibility permissions enabled for the Python interpreter.

Setting Up Accessibility Permissions:

1. Go to **System Preferences > Security & Privacy > Privacy**.
2. Select **Accessibility** in the left panel.
3. Unlock to make changes, then add your Python interpreter (e.g., `/usr/local/bin/python3`).


IMPORTANT: Disclaimer
---------------------

**Full System Access**: This package grants access to system applications and data, including the ability to read data
from applications, interact with their user interfaces, and access minimized or backgrounded apps. Exercise caution to
prevent unintentional exposure of sensitive information or unintended actions, especially when using the package with an
AI agent or automation.

**Data Privacy**: Avoid leaking personal or sensitive information, such as passwords or private files, especially when
integrating with external services or APIs.

**Require User Confirmation**: For safety and control, no action should be executed by AI agents or automations without
explicit user confirmation.

.. toctree::
   :maxdepth: 4
   :caption: Contents:

   py2mac
   py2mac.langchain_py2mac
