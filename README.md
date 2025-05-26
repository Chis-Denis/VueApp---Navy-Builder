# Naval Ships Management System

A full-stack web application for managing and tracking naval ships, built with FastAPI and Vue.js.

## 🚀 Features

- **Real-time Ship Management**
  - Add, edit, and delete naval ships
  - Advanced filtering and sorting capabilities

- **Authentication & Security**
  - User authentication and authorization
  - Secure password handling
  - Protected API endpoints

- **Data Visualization**
  - Ship statistics and analytics
  - Interactive charts and graphs
  - Service duration calculations

- **File Management**
  - Upload and download files
  - File listing and management
  - Secure file storage

## 🛠️ Tech Stack

### Backend
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- Uvicorn (ASGI server)
- Python-Jose (JWT tokens)
- Passlib (Password hashing)
- SQLite (Database)
- Railway (Deployment platform)

### Frontend
- Vue.js 3
- Vue Router
- Axios (HTTP client)
- Chart.js (Data visualization)
- Vite (Build tool)
- Vercel (Deployment platform)

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+
- npm or yarn

## 🚀 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd naval-ships-management
```

2. Set up the backend:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. Set up the frontend:
```bash
cd Frontend
npm install
```

## 🏃‍♂️ Running the Application

### Local Development

1. Start the backend server:
```bash
python run_server.py
```
The server will start at `http://localhost:8000`

2. Start the frontend development server:
```bash
cd Frontend
npm run serve
```
The frontend will be available at `http://localhost:8080`

### Production Deployment

The application is deployed and accessible at:
- Frontend: [Vercel Deployment URL]
- Backend: [Railway Deployment URL]

## 🧪 Testing

### Backend Tests
```bash
pytest Backend/tests/
```

### Frontend Tests
```bash
cd Frontend
npm run test
```

## 📚 API Documentation

The API documentation is available at:
- Swagger UI: `[Railway Backend URL]/docs`
- ReDoc: `[Railway Backend URL]/redoc`

## 🔒 Environment Variables

Create a `.env` file in the root directory with the following variables:
```
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For production deployment on Railway, these environment variables should be configured in the Railway dashboard.

## 📝 Project Structure

```
├── Backend/
│   ├── main.py           # Main FastAPI application
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── Frontend/
│   ├── src/             # Vue.js source code
│   ├── public/          # Static assets
│   └── tests/           # Frontend tests
├── database/
│   ├── models.py        # Database models
│   └── database.py      # Database configuration
├── requirements.txt     # Python dependencies
└── run_server.py       # Server entry point
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Chis Denis - Initial work

## 🙏 Acknowledgments

- FastAPI documentation
- Vue.js documentation
- SQLAlchemy documentation 