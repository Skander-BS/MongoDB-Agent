# MongoDB-Agent

A natural language MongoDB query agent powered by **LangChain** and **Groq**, with a **Streamlit** frontend.

## 🚀 Features

- Query your MongoDB database using **human language**.
- Utilizes **LangChain** for query processing.
- Powered by **Groq** for LLM support.
- Simple and intuitive **Streamlit** frontend.
- Cross-platform support (**Windows, macOS, Ubuntu**).

## 🛠 Installation

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Skander-BS/MongoDB-Agent.git
cd MongoDB-Agent
```

### 2️⃣ Update environment variables

Configure your `.env` file with:

- **MongoDB URI** (`DATABASE_URI`)
- **Groq API settings** (`GROQ_API_KEY`, etc..)

Recommended to use a llama3.3-70b Model.
Further model supports will be added in te future.

### 3️⃣ Initialize the environment

Run:

```bash
make init
```

This will:

- Create a **virtual environment**.
- Install all **dependencies**.

Supports **Windows**, **macOS**, and **Ubuntu**.

### 4️⃣ Start the application

Run:

```bash
make start
```

This will **launch the Streamlit app and the uvicorn server**.

### 5️⃣ Stop the application

After shutting down, clean up any remaining processes:

```bash
make stop
```

### 5️⃣ Demo

[Watch the demo](https://raw.githubusercontent.com/Skander-BS/MongoDB-Agent/main/src/media/demo.mp4)

## 📜 License

This project is licensed under MIT Licence.

---
Made with ❤️ by Skander BS 
