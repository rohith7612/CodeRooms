<h1 align="center">⚔️ CodeRooms</h1>

<p align="center">
  <img src="https://img.shields.io/github/languages/top/rohith7612/CodeRooms?style=flat-square" alt="Top Language">
  <img src="https://img.shields.io/github/repo-size/rohith7612/CodeRooms?style=flat-square" alt="Repo Size">
  <img src="https://img.shields.io/github/issues/rohith7612/CodeRooms?style=flat-square" alt="Issues">
  <img src="https://img.shields.io/github/license/rohith7612/CodeRooms?style=flat-square" alt="License">
</p>

<br>
<p align="center">
  <b>A real-time multiplayer competitive coding platform where developers can race against each other to solve algorithmic problems, built with Django and WebSockets for seamless live synchronization.</b>
</p>

---

## 🚀 Features

*   ⚡ **Real-time Coding Arena**: Live updates of opponent progress, test cases passed, and scores.
*   👥 **Multiplayer Lobbies**: Create or join match rooms via unique 6-character Room IDs.
*   🏆 **Live Leaderboard**: Dynamic ranking updates as participants submit and run their code.
*   👀 **Spectator Mode**: Watch ongoing matches live without participating, seeing real-time coding strategies.
*   🤖 **AI Problem Generation**: Generates unique, tailored coding problems using OpenAI integration.
*   🛡️ **Anti-Cheat System**: Optional feature to detect and alert the lobby if participants switch tabs during a match.
*   📊 **User Dashboard**: Keep track of your stats (wins, rating, topic strength) and past match history.
*   🔐 **Admin Panel**: Efficient management of rooms, users, and global cheat detection settings.

---

## 🛠️ Tech Stack

### Backend
*   **Framework**: [Python 3](https://www.python.org/) & [Django](https://www.djangoproject.com/)
*   **WebSockets**: [Django Channels](https://channels.readthedocs.io/) & ASGI Server (Daphne)
*   **AI Integration**: [OpenAI API](https://openai.com/)
*   **Database**: SQLite (Development)

### Frontend
*   **Stack**: HTML5, CSS3, JavaScript
*   **Code Editor Engine**: Monaco Editor (VS Code's underlying editor engine)

### Deployment
*   **Configuration**: Supports automated deployment via `render.yaml`
*   **Production Server**: Gunicorn & Daphne
*   **Static Files**: WhiteNoise

---

## ⚙️ Setup & Installation

Follow these steps to set up the project locally for development or testing:

1.  **Clone the repository**
    ```bash
    git clone https://github.com/rohith7612/CodeRooms.git
    cd CodeRooms
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment Variables**
    Create a `.env` file in the root directory and add any required environment variables (e.g., `OPENAI_API_KEY`, `SECRET_KEY`).

5.  **Apply database migrations**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server via ASGI**
    Because this project uses Django Channels for WebSockets, it runs via ASGI:
    ```bash
    python manage.py runserver
    ```
    Access the application at: `http://127.0.0.1:8000`

---

## 🎮 How to Play

1.  **Sign Up / Login**: Create an account to track your global rating.
2.  **Create a Room**: Choose a problem topic (e.g., Arrays, Dynamic Programming) and difficulty.
3.  **Invite Friends**: Share the generated 6-character Room ID.
4.  **Start Match**: As the host, click "Start Game" once everyone is in.
5.  **Race!**: Solve the provided algorithmic problem before others. Note: You have 3 attempts!
6.  **Game Over**: View the final leaderboard, code analysis, and solution breakdown.

---

## 🛡️ Anti-Cheat Details

The platform includes an Anti-cheat monitoring system that can be toggled per room in the Admin Panel (`/admin`).
When enabled, the system continuously monitors:
*   **Tab Switching**: Instantly alerts the entire lobby if a user leaves the competition tab to search the web or view other applications.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! 
Feel free to check out the [issues page](https://github.com/rohith7612/CodeRooms/issues).
For major changes, please open an issue first to discuss what you would like to change.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

Distributed under the MIT License.