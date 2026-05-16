# 🚀 Smart Resume Screener - AI-Powered Recruitment Platform

An advanced AI-powered resume screening and candidate ranking system that leverages large language models like GPT-4o-mini for intelligent analysis, with a modern glass-morphism UI and comprehensive workflow management.

![Smart Resume Screener](https://img.shields.io/badge/AI-Powered-blue) ![Flask](https://img.shields.io/badge/Flask-2.3+-green) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange) ![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

### 🤖 Advanced AI Resume Analysis
- **GPT-5 Integration**: Uses OpenAI's latest model for intelligent resume parsing
- **Smart Analysis**: Provides detailed candidate summaries and professional insights
- **Quality Scoring**: AI-generated quality scores with comprehensive explanations
- **Bias-Free Assessment**: Objective AI analysis reduces human bias in screening

### 🎯 Intelligent Job Matching System
- **AI-Powered Scoring**: Candidates scored on overall fit, skills match, and experience match
- **Detailed Explanations**: The AI model provides comprehensive analysis of why candidates match or don't match
- **Transparent Scoring**: Shows key strengths, areas for improvement, and hiring recommendations
- **Multiple Ranking Models**: Choose between AI-enhanced, traditional semantic, or baseline TF-IDF models

### 🎨 Professional Dashboard Interface
- **Modern Design**: Futuristic UI with glass-morphism effects and professional gradients
- **Intuitive Navigation**: Four-tab system (Dashboard, Upload, Candidates, Jobs)
- **Real-time Stats**: Live dashboard showing candidates, jobs, and screening sessions
- **Responsive Design**: Works seamlessly across desktop and mobile devices

### 📋 Complete Workflow Management
- **Resume Upload**: Drag-and-drop interface with multi-file support
- **Job Creation**: Comprehensive job description forms with skill tagging
- **AI Screening**: One-click screening with real-time progress indicators
- **Results Visualization**: Detailed candidate rankings with scoring breakdowns

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- OpenAI API Key (for AI features)
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-resume-screener.git
cd smart-resume-screener
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model
```bash
python -m spacy download en_core_web_sm
```

### 5. Environment Configuration
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` file:
```env
# Database configuration
DATABASE_URL=sqlite:///d:/SmartScreener/instance/smartscreener.db

# Session secret key for Flask session management
SESSION_SECRET=your-super-secret-key-here

# Embedding model (optional, defaults to all-MiniLM-L6-v2)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# OpenAI API configuration (REQUIRED for AI features)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 6. Initialize Database
```bash
python init_db.py
```

### 7. Run Database Migrations
```bash
python migrations/003_add_ai_analysis_fields.py
```

### 8. Create Admin User (Optional)
```bash
python create_admin.py
```

### 9. Start the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🔧 Configuration

### OpenAI API Setup
1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file as `OPENAI_API_KEY`
3. Choose your preferred model (gpt-4o-mini recommended for cost-effectiveness)

### Database Configuration
- **SQLite** (default): Perfect for development and small deployments
- **MySQL**: For production environments, update `DATABASE_URL` accordingly

## 🚀 Usage Guide

### 1. Dashboard Overview
- Access the main dashboard at `/dashboard`
- View real-time statistics and workflow progress
- Quick access to all major features

### 2. Upload Resumes
- Navigate to Upload page or use the dashboard
- Drag and drop PDF/DOCX files or click to browse
- AI analysis runs automatically on upload
- View progress indicators during processing

### 3. Create Job Descriptions
- Define job requirements and skills
- Set experience and education criteria
- AI will use this for intelligent matching

### 4. AI Screening Process
- Select a job description
- Choose ranking model (AI-enhanced recommended)
- View detailed candidate rankings with explanations
- Get hiring recommendations and insights

### 5. Review Results
- Detailed candidate profiles with AI insights
- Skill matching analysis
- Quality scores and recommendations
- Export capabilities for further processing

## 🎨 UI Features

### Glass-Morphism Design
- Modern frosted glass effects
- Smooth animations and transitions
- Professional gradient backgrounds
- Responsive layout for all devices

### Interactive Elements
- Drag-and-drop file uploads
- Real-time progress indicators
- Animated statistics counters
- Hover effects and micro-interactions

### Accessibility
- High contrast ratios
- Keyboard navigation support
- Screen reader compatibility
- Mobile-first responsive design

## 🤖 AI Capabilities

### Resume Analysis
- **Professional Summary**: AI-generated candidate summaries
- **Key Strengths**: Identified core competencies
- **Areas for Improvement**: Constructive feedback
- **Career Progression**: Analysis of professional growth
- **Technical Expertise**: Skill level assessment
- **Quality Scoring**: Overall candidate quality (0-100)

### Job Matching
- **Overall Match Score**: Comprehensive fit assessment
- **Skills Analysis**: Detailed skill matching with explanations
- **Experience Evaluation**: Years and relevance assessment
- **Education Matching**: Degree and field compatibility
- **Cultural Fit**: Soft skills and personality indicators
- **Hiring Recommendations**: Clear guidance (Strong Recommend/Recommend/Consider/Not Recommend)

### Bias Mitigation
- Objective AI assessment
- Demographic parity monitoring
- Fairness metrics tracking
- Transparent scoring methodology

## 📊 Analytics & Reporting

### Dashboard Metrics
- Total candidates processed
- AI analysis coverage
- Average quality scores
- Job matching statistics

### Quality Distribution
- Visual charts showing candidate quality spread
- Performance trends over time
- Comparative analysis capabilities

### Export Features
- Candidate data export
- Ranking results download
- Analytics report generation

## 🔒 Security & Privacy

### Data Protection
- Secure file upload handling
- Encrypted data storage
- Privacy-compliant processing
- GDPR considerations

### User Management
- Role-based access control
- Admin and user permissions
- Session management
- Rate limiting protection

## 🧪 Testing

### Run Tests
```bash
python -m pytest tests/
```

### Test Coverage
```bash
python -m pytest --cov=. tests/
```

### Manual Testing
1. Upload sample resumes
2. Create test job descriptions
3. Run AI screening process
4. Verify results accuracy

## 🚀 Deployment

### Production Setup
1. Use a production WSGI server (Gunicorn recommended)
2. Configure environment variables
3. Set up proper database (MySQL/PostgreSQL)
4. Enable HTTPS
5. Configure monitoring and logging

### Docker Deployment
```bash
# Build image
docker build -t smart-resume-screener .

# Run container
docker run -p 5000:5000 --env-file .env smart-resume-screener
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
 
## 🙏 Acknowledgments

- OpenAI for their powerful APIs
- spaCy for NLP processing
- Sentence Transformers for embeddings
- Bootstrap for UI components
- Flask community for the excellent framework

## 📞 Support

For support, email support@smartscreener.com or create an issue on GitHub.

## 🔄 Changelog

### Version 2.0.0 (Latest)
- ✅ GPT-4o-mini integration for advanced AI analysis
- ✅ Modern glass-morphism UI design
- ✅ Comprehensive workflow management
- ✅ Real-time progress indicators
- ✅ Enhanced drag-and-drop interface
- ✅ Detailed AI insights and explanations
- ✅ Multiple ranking algorithms
- ✅ Professional dashboard with analytics

### Version 1.0.0
- Basic resume parsing
- Simple candidate ranking
- Traditional UI design
- Basic job matching

---

**Made with ❤️ by Harshal Dhangar**

*Transforming recruitment with AI-powered intelligence*
