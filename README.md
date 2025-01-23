<readme>
  <title>IntelliGrade</title>
  <description>A powerful AI system for intelligent handwritten answer script evaluation, combining speed, accuracy, and reliability using Google's Gemini 1.5 Flash model for visual question answering and handwriting OCR.</description>

  <flow>
    <image>flow.jpg</image>
  </flow>

  <setup>
    <step>Clone the Repository</step>
    <command>
      git clone https://github.com/yourusername/image-text-extractor.git](https://github.com/ShiroYasha18/ibm_dpk-project
      cd ibm_dpk-project
    </command>

    <step>Set Up Virtual Environment</step>
    <command>For Windows:</command>
    <command>
      python -m venv venv
      .\venv\Scripts\activate
    </command>
    <command>For macOS/Linux:</command>
    <command>
      python3 -m venv venv
      source venv/bin/activate
    </command>

    <step>Install Requirements</step>
    <command>pip install -r requirements.txt</command>

    <step>Get Google Generative AI API Key</step>
    <instructions>
      <item>Go to <link>https://console.cloud.google.com/</link></item>
      <item>Enable the Generative AI API</item>
      <item>Generate an API key from the "Credentials" section</item>
      <item>Copy your API key</item>
    </instructions>

    <step>Set Up Environment Variables</step>
    <instructions>
      <item>Create a file named `.env` in the project root directory</item>
      <item>Add the API key as:
        <code>GOOGLE_API_KEY="your_api_key_here"</code>
      </item>
    </instructions>

    <step>Run the Application</step>
    <command>python image_processor.py</command>
  </setup>

  <requirements>
    <note>See `requirements.txt` for a full list of dependencies</note>
  </requirements>

  <notes>
    <item>The AI utilizes Google's Gemini 1.5 Flash model, a powerful tool within the Generative AI API, for both visual question answering and accurate handwriting OCR.</item>
    <item>Keep your `.env` file confidential and never commit it to version control.</item>
    <item>Supported image formats: PNG, JPEG</item>
    <item>Exclude the `venv` folder from version control.</item>
  </notes>

  <troubleshooting>
    <item>Ensure your virtual environment is activated.</item>
    <item>Verify your Google Generative AI API key is correct.</item>
    <item>Check the location of your `.env` file.</item>
    <item>Make sure all dependencies are installed correctly.</item>
  </troubleshooting>

  <contributing>
    <steps>
      <step>Fork the repository</step>
      <step>Create a feature branch: <code>git checkout -b feature/AmazingFeature</code></step>
      <step>Commit your changes: <code>git commit -m 'Add some AmazingFeature'</code></step>
      <step>Push to the branch: <code>git push origin feature/AmazingFeature</code></step>
      <step>Open a Pull Request</step>
    </steps>
  </contributing>

  <license>This project is licensed under the MIT License. See the LICENSE file for details.</license>
</readme>
