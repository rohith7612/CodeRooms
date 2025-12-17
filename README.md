# ⚔️ CodeRooms

**CodeRooms** is a real-time multiplayer competitive coding platform where developers can race against each other to solve algorithmic problems. Built with Django and WebSockets for seamless live synchronization.

## 🚀 Features

*   **Real-time Coding Arena**: Live updates of opponent progress (test cases passed, score).
*   **Multiplayer Lobbies**: Create or join rooms via unique Room IDs.
*   **Live Leaderboard**: Dynamic ranking updates as participants submit code.
*   **Spectator Mode**: Watch ongoing matches live without participating.
*   **Anti-Cheat System**: (Optional) Detects and alerts if participants switch tabs during a match.
*   **User Dashboard**: Track your stats (wins, rating, topic strength) and match history.
*   **AI Problem Generation**: (Optional) Generate unique problems using OpenAI.
*   **Admin Panel**: Efficient management of rooms, users, and cheat detection settings.

## 🛠️ Tech Stack

*   **Backend**: Python, Django, Django Channels (WebSockets).
*   **Frontend**: HTML5, CSS3, JavaScript.
*   **Editor**: Monaco Editor (VS Code's editor engine).
*   **Database**: SQLite (Development).
*   **Server**: Daphne / ASGI.

## ⚙️ Setup & Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/coderooms.git
    cd coderooms
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

4.  **Apply database migrations**
    ```bash
    python manage.py runserver
    # Run migrations using migrate
    python manage.py migrate
    ```

5.  **Run the development server**
    ```bash
    python manage.py runserver
    ```
    Access the app at `http://127.0.0.1:8000`.

## 🎮 How to Play

1.  **Sign Up / Login**: Create an account to track your rating.
2.  **Create a Room**: Choose a topic (e.g., Arrays, DP) and difficulty.
3.  **Invite Friends**: Share the 6-character Room ID.
4.  **Start Match**: As the host, click "Start Game".
5.  **Race!**: Solve the problem before others. You have 3 attempts!
6.  **Game Over**: View the final leaderboard and analysis.

## 🛡️ Anti-Cheat

Anti-cheat can be toggled per room in the Admin Panel (`/admin`). When enabled, the system monitors:
*   **Tab Switching**: Alerts the lobby if a user leaves the tab.

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

[MIT](https://choosealicense.com/licenses/mit/)
