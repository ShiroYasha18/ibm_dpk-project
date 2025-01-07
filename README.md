# IntelliGrade

 A powerful AI system for intelligent answer script evaluation, combining speed, accuracy, and reliability.
 ## Flow
 ![Uploading Untitled (Draft)-1.jpg…]()


## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/image-text-extractor.git](https://github.com/ShiroYasha18/ibm_dpk-project
cd ibm_dpk-project
```

### 2. Set Up Virtual Environment

For Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

For macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements

```bash
pip install -r requirements.txt
```

### 4. Get Groq API Key

1. Go to [Groq's website](https://console.groq.com/)
2. Sign up or log in to your account
3. Navigate to API section
4. Generate a new API key
5. Copy your API key

### 5. Set Up Environment Variables

1. Create a new file named `.env` in the project root directory
2. Add your Groq API key to the `.env` file:
```
GROQ_API_KEY="your_api_key_here"
```
3. Save the file

### 6. Running the Application

```bash
python image_processor.py
```



## Requirements

See `requirements.txt` for a full list of dependencies

## Notes

- Keep your `.env` file private and never commit it to version control
- Make sure your images are in a supported format (JPEG, PNG)
- The virtual environment folder (`venv`) should also be excluded from version control

## Troubleshooting

If you encounter issues:
1. Ensure your virtual environment is activated
2. Verify your Groq API key is correct
3. Check that your `.env` file is in the correct location
4. Make sure all dependencies are installed correctly

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details
