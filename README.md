# ARNO Planner - AI-Powered Scheduling Solution

ARNO Planner is a sophisticated scheduling and timetabling application that leverages artificial intelligence to solve complex planning problems. It provides an intuitive interface for managing educational and organizational scheduling needs.

## 🚀 Key Features

- **AI-Powered Optimization**: Uses OptaPlanner's constraint solving algorithms
- **Natural Language Processing**: Understands scheduling requests in plain language
- **Real-time Updates**: Instant visualization of scheduling solutions
- **Multi-view Timetables**: View schedules by Room, Teacher, or Student Group
- **Responsive Design**: Modern, mobile-friendly interface
- **Interactive UI**: Drag-and-drop functionality and real-time updates

## 🛠️ Technology Stack

### Frontend
- **Next.js 14** - React framework with server-side rendering
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations and transitions
- **Shadcn/ui** - High-quality UI components
- **Radix UI** - Accessible component primitives

### Backend
- **FastAPI** - Modern, fast Python web framework
- **OptaPy** - AI constraint solver for Python
- **LangChain** - Framework for developing LLM applications
- **OpenAI Integration** - Natural language processing capabilities

### Infrastructure
- **Docker** - Containerization and deployment
- **Docker Compose** - Multi-container orchestration
- **Python 3.10** - Backend runtime
- **Node.js 20** - Frontend runtime

## 🏗️ Architecture

The application follows a microservices architecture with:
- Frontend service (Next.js)
- Backend service (FastAPI)
- AI optimization engine (OptaPy)
- Natural language processing service (LangChain)

## 🚦 Getting Started

1. Clone the repository
2. Create a `.env` file with your OpenAI API key:

```bash
OPENAI_API_KEY='your openai api key here'
```

Then run the containers with the following command:

```bash
docker-compose up --build # first time
```

```bash
docker-compose up # next times
```

To stop the containers:

```bash
docker-compose down
```
