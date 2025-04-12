🚀 Quick Start
Prerequisites
Python 3.8+
SQL Database
Ollama
Installation
bash
# Clone the repository
git clone https://github.com/gauravchand/Optimizing-Retail-Inventory-with-Multi-Agents.git
cd retail-inventory-ai

# Install dependencies
pip install -r requirements.txt

# Initialize database
python setup_db.py

# Start the application
python main.py
The dashboard will be available on your local port after running these commands.

📂 Project Structure
Code
retail-inventory-ai/
├── app/
│   ├── agents/         # Agent implementation
│   ├── config/         # Configuration files
│   ├── models/         # Data models
│   ├── templates/      # UI templates
│   └── services/       # Business logic
├── config.py          # Main configuration
├── main.py           # Entry point
└── setup_db.py       # Database setup
🛠 Technical Stack
Backend: Python
Database: SQL
AI Framework: Ollama
Interface: Web Dashboard
🔑 Key Features
Automated Inventory Management

Real-time stock monitoring
Intelligent restocking decisions
Supply chain optimization
Multi-Agent Architecture

Store agents
Supplier agents
Coordination layer
Business Intelligence

Real-time analytics
Predictive insights
Performance monitoring
💡 Benefits
Reduced operational costs
Optimized stock levels
Improved customer satisfaction
Enhanced supply chain visibility
Data-driven decision making
🔧 Configuration
Update .env file with your database credentials
Configure agent parameters in config.py
Adjust business rules in the agents' configuration
📊 Dashboard Access
After running the application, access the dashboard at:

Code
http://localhost:<port>
🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

✍️ Authors
Gaurav Chand (@gauravchand)
Akarshan Gupta (@AkarshanGupta)
