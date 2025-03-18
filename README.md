# Motorcycle Inspection Video Analyzer

A Streamlit web application that analyzes motorcycle inspection videos using Google's Gemini 1.5 Pro Vision model to provide detailed damage assessment and mechanical analysis.

## Features

- Comprehensive motorcycle inspection analysis using Gemini 1.5 Pro Vision AI
- Detailed damage assessment and inventory
- Engine condition analysis based on visual and audio cues
- Modification and aftermarket parts detection
- Repair priority recommendations with safety ratings
- High-resolution frame analysis (1024x1024)

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Get an API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. Create a `.env` file in the root directory and add your API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the App

1. Run the Streamlit app:
   ```bash
   streamlit run main.py
   ```
2. Open your browser and navigate to the provided local URL
3. Enter a YouTube URL of a motorcycle inspection video
4. Click "Analyze Video" to start the inspection

## Analysis Output

The app provides a structured analysis including:

1. Overall Assessment
   - Condition score (0-10)
   - Estimated age
   - Engine health score

2. Damage Inventory
   - Type and location of damage
   - Severity assessment
   - Repair impact and cost estimates

3. Engine Assessment
   - Sound analysis
   - Performance indicators
   - Maintenance recommendations

4. Modification Assessment
   - Aftermarket parts identification
   - Missing stock parts
   - Impact on value

5. Repair Priorities
   - Urgency levels
   - Safety-critical issues

## Technical Details

- Uses Gemini 1.5 Pro Vision for advanced visual analysis
- Processes 12 high-resolution frames for comprehensive coverage
- Implements structured JSON output for consistent analysis
- Automatic cleanup of temporary files
- Environment variable based configuration

## Note

- The app requires an active internet connection
- Processing time depends on video length and complexity
- Temporary video files are automatically cleaned up after processing
- Make sure your Google AI API key has access to Gemini 1.5 Pro
- For best results, use high-quality inspection videos with clear audio 