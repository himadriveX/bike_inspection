import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
from PIL import Image
import tempfile
import time
import json
from dotenv import load_dotenv
import numpy as np
import cv2
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(page_title="Motorcycle Inspection Analyzer", layout="wide")

# Title and description
st.title("Motorcycle Inspection Video Analyzer")
st.markdown("""
This app analyzes motorcycle inspection videos using Google's Gemini 1.5 Pro Vision model to provide:
1. Comprehensive damage assessment
2. Engine condition analysis
3. Modification evaluation
4. Repair priorities
""")

# Initialize Gemini model
def initialize_gemini():
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        st.error("Google API Key not found in environment variables!")
        return None
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-vision')
    return model

# Helper function to process video buffer
def process_video_buffer(video_path):
    try:
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Error opening video file")

        # Get video properties
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        duration = total_frames / fps

        # Process video in chunks
        chunk_size = 30  # Process 1 second at a time (assuming 30fps)
        chunks = []
        frame_buffers = []
        
        for chunk_start in range(0, total_frames, chunk_size):
            chunk_end = min(chunk_start + chunk_size, total_frames)
            chunk_frames = []
            
            # Read frames for this chunk
            for frame_idx in range(chunk_start, chunk_end):
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Convert to PIL Image
                frame_pil = Image.fromarray(frame_rgb)
                # Resize while maintaining aspect ratio
                frame_pil.thumbnail((1024, 1024))
                chunk_frames.append(frame_pil)
            
            if chunk_frames:
                chunks.append(chunk_frames)
                # Create a composite image for this chunk
                if len(chunk_frames) > 1:
                    # Create a grid of frames
                    grid_size = int(np.ceil(np.sqrt(len(chunk_frames))))
                    grid_image = Image.new('RGB', (1024 * grid_size, 1024 * grid_size))
                    
                    for idx, frame in enumerate(chunk_frames):
                        x = (idx % grid_size) * 1024
                        y = (idx // grid_size) * 1024
                        grid_image.paste(frame, (x, y))
                    
                    frame_buffers.append(grid_image)
                else:
                    frame_buffers.append(chunk_frames[0])

        cap.release()
        return frame_buffers, duration, fps

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        return None, None, None

# Helper function to handle uploaded file
@st.cache_data
def handle_uploaded_file(uploaded_file):
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        
        # Get the file name and extension
        file_name, file_extension = os.path.splitext(uploaded_file.name)
        
        # Define the path where the file will be saved
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save the uploaded file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # For images, we can generate a thumbnail
        thumbnail_url = None
        if file_extension.lower() in ['.jpg', '.jpeg', '.png', '.gif']:
            with Image.open(file_path) as img:
                img.thumbnail((128, 128))
                thumbnail_path = os.path.join(temp_dir, f"{file_name}_thumb{file_extension}")
                img.save(thumbnail_path)
                thumbnail_url = thumbnail_path
        
        return file_name, file_path, thumbnail_url
    except Exception as e:
        st.error(f"Error handling uploaded file: {str(e)}")
        return None, None, None

# Function to analyze video with Gemini
def analyze_motorcycle_inspection(model, frame_buffers):
    prompt = """Analyze this motorcycle inspection video carefully and provide a comprehensive damage assessment.
Only base your analysis strictly on what information is available in the video.
Be thorough in identifying all visible and audible issues.

For each identified issue, assess:
Type of damage (dent, scratch, rust, missing part, etc.)
Severity (minor, moderate, severe)
Location on the motorcycle
Estimated repair/replacement cost impact

Pay special attention to:
Structural damage (frame, forks, swingarm)
Engine condition (based on sound analysis)
Missing or aftermarket parts
Paint condition (scratches, chips, fading)
Rust or corrosion
Modifications from stock configuration
Mechanical issues detectable from engine sound (knocking, ticking, irregular idle)

For engine sound analysis:
Assess cold start behavior
Evaluate idle stability
Note any unusual sounds at different RPMs
Estimate engine health and approximate age based on sound characteristics
Identify potential mechanical issues"""
    
    try:
        # Process each buffer with Gemini
        all_analyses = []
        for buffer in frame_buffers:
            response = model.generate_content([prompt, buffer])
            all_analyses.append(response.text)
        
        # Combine all analyses
        combined_analysis = {
            "overall_assessment": {
                "condition_score": 0,
                "estimated_age": "",
                "engine_health_score": 0
            },
            "damage_inventory": [],
            "engine_assessment": {
                "sound_characteristics": "",
                "identified_issues": [],
                "performance_indicators": [],
                "maintenance_recommendations": []
            },
            "modification_assessment": {
                "aftermarket_parts": [],
                "missing_stock_parts": [],
                "modification_impact": ""
            },
            "repair_priority": []
        }
        
        # Try to parse each analysis and combine them
        for analysis_text in all_analyses:
            try:
                parsed = json.loads(analysis_text)
                # Merge the analyses (you might want to implement more sophisticated merging logic)
                combined_analysis["overall_assessment"]["condition_score"] = max(
                    combined_analysis["overall_assessment"]["condition_score"],
                    parsed.get("overall_assessment", {}).get("condition_score", 0)
                )
                combined_analysis["damage_inventory"].extend(
                    parsed.get("damage_inventory", [])
                )
                combined_analysis["engine_assessment"]["identified_issues"].extend(
                    parsed.get("engine_assessment", {}).get("identified_issues", [])
                )
                combined_analysis["modification_assessment"]["aftermarket_parts"].extend(
                    parsed.get("modification_assessment", {}).get("aftermarket_parts", [])
                )
                combined_analysis["repair_priority"].extend(
                    parsed.get("repair_priority", [])
                )
            except json.JSONDecodeError:
                # If parsing fails, add raw analysis
                combined_analysis["raw_analyses"] = combined_analysis.get("raw_analyses", []) + [analysis_text]
        
        return combined_analysis
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

# Main app interface
model = initialize_gemini()

if model:
    # File upload section
    st.subheader("Upload Motorcycle Inspection Video")
    uploaded_file = st.file_uploader("Choose a video file", type=["mp4"])
    
    if uploaded_file is not None:
        title, file_path, thumbnail_url = handle_uploaded_file(uploaded_file)
        if file_path:
            st.success(f"File '{title}' uploaded successfully!")
            if thumbnail_url:
                st.image(thumbnail_url, caption="Thumbnail")
            
            if st.button("Analyze Video"):
                with st.spinner("Processing video..."):
                    # Process video buffer
                    frame_buffers, duration, fps = process_video_buffer(file_path)
                    
                    if frame_buffers:
                        # Create layout
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.subheader("Video Analysis Buffers")
                            # Display processed buffers
                            for i, buffer in enumerate(frame_buffers):
                                st.image(buffer, caption=f"Buffer {i+1}", use_column_width=True)
                        
                        # Analyze with Gemini
                        analysis = analyze_motorcycle_inspection(model, frame_buffers)
                        
                        with col2:
                            st.subheader("Inspection Results")
                            if analysis:
                                # Overall Assessment
                                st.markdown("### Overall Assessment")
                                st.write(f"Condition Score: {analysis['overall_assessment']['condition_score']}/10")
                                st.write(f"Estimated Age: {analysis['overall_assessment']['estimated_age']}")
                                st.write(f"Engine Health: {analysis['overall_assessment']['engine_health_score']}/10")
                                
                                # Damage Inventory
                                st.markdown("### Damage Inventory")
                                for damage in analysis['damage_inventory']:
                                    with st.expander(f"{damage['damage_type']} - {damage['location']}"):
                                        st.write(f"Severity: {damage['severity']}")
                                        st.write(f"Description: {damage['description']}")
                                        st.write(f"Repair Impact: {damage['repair_impact']}")
                                        st.write(f"Estimated Cost: {damage['estimated_cost']}")
                                
                                # Engine Assessment
                                st.markdown("### Engine Assessment")
                                st.write(f"Sound Characteristics: {analysis['engine_assessment']['sound_characteristics']}")
                                st.write("Issues:", ", ".join(analysis['engine_assessment']['identified_issues']))
                                
                                # Modifications
                                st.markdown("### Modifications")
                                st.write("Aftermarket Parts:", ", ".join(analysis['modification_assessment']['aftermarket_parts']))
                                st.write("Impact:", analysis['modification_assessment']['modification_impact'])
                                
                                # Repair Priorities
                                st.markdown("### Repair Priorities")
                                for repair in analysis['repair_priority']:
                                    st.write(f"- {repair['item']} (Urgency: {repair['urgency']}, Safety Critical: {repair['safety_critical']})")
                        
                        # Cleanup
                        if os.path.exists(file_path):
                            os.remove(file_path)
else:
    st.error("Please set the GOOGLE_API_KEY in your .env file to use this application.")
