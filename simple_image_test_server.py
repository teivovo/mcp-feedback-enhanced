#!/usr/bin/env python3
"""
Simple Image Test Server for MCP Feedback Enhanced

This creates a minimal test server on port 8772 to test the fixed image processing
without the complexity of the full MCP server.

Usage:
    python simple_image_test_server.py
"""

import asyncio
import base64
import json
import sys
from pathlib import Path
from typing import List, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastmcp.utilities.types import Image
import uvicorn


app = FastAPI(title="Simple Image Test Server")


@app.get("/")
async def get_test_page():
    """Serve a simple test page for image upload"""
    html = """
<!DOCTYPE html>
<html>
<head>
    <title>Image Processing Test - Port 8772</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .upload-area { border: 2px dashed #ccc; padding: 40px; text-align: center; margin: 20px 0; }
        .upload-area.dragover { border-color: #007bff; background-color: #f8f9fa; }
        .results { margin-top: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 5px; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; background-color: #007bff; color: white; }
        #imagePreview { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 20px; }
        .image-item { border: 1px solid #ddd; padding: 10px; border-radius: 5px; max-width: 300px; }
        .image-item img { max-width: 100%; height: auto; }
    </style>
</head>
<body>
    <h1>Image Processing Test Server</h1>
    <p><strong>Port:</strong> 8772 (Independent test environment)</p>
    <p><strong>Status:</strong> Testing fixed FastMCP Image processing</p>
    
    <div class="upload-area" id="uploadArea">
        <p>Drag & drop images here or click to select</p>
        <input type="file" id="fileInput" multiple accept="image/*" style="display: none;">
        <button onclick="document.getElementById('fileInput').click()">Select Images</button>
    </div>
    
    <button onclick="testImageProcessing()">Test Image Processing</button>
    <button onclick="clearResults()">Clear Results</button>
    
    <div id="imagePreview"></div>
    <div id="results" class="results" style="display: none;"></div>
    
    <script>
        let uploadedImages = [];
        
        // Setup drag and drop
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(e.target.files);
        });
        
        function handleFiles(files) {
            uploadedImages = [];
            const preview = document.getElementById('imagePreview');
            preview.innerHTML = '';
            
            Array.from(files).forEach((file, index) => {
                if (file.type.startsWith('image/')) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        const imageData = {
                            name: file.name,
                            type: file.type,
                            size: file.size,
                            data: e.target.result.split(',')[1] // Remove data URL prefix
                        };
                        uploadedImages.push(imageData);
                        
                        // Add to preview
                        const div = document.createElement('div');
                        div.className = 'image-item';
                        div.innerHTML = `
                            <img src="${e.target.result}" alt="${file.name}">
                            <p><strong>${file.name}</strong></p>
                            <p>Type: ${file.type}</p>
                            <p>Size: ${file.size} bytes</p>
                        `;
                        preview.appendChild(div);
                    };
                    reader.readAsDataURL(file);
                }
            });
        }
        
        async function testImageProcessing() {
            if (uploadedImages.length === 0) {
                alert('Please upload some images first!');
                return;
            }
            
            try {
                const response = await fetch('/test-images', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ images: uploadedImages })
                });
                
                const result = await response.json();
                displayResults(result);
            } catch (error) {
                displayResults({ error: error.message });
            }
        }
        
        function displayResults(result) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.style.display = 'block';
            
            let html = '<h3>Test Results</h3>';
            
            if (result.error) {
                html += `<p class="error">ERROR: ${result.error}</p>`;
            } else {
                html += `<p class="success">SUCCESS: Processed ${result.processed_count} images</p>`;
                if (result.details) {
                    html += '<h4>Details:</h4><ul>';
                    result.details.forEach(detail => {
                        const className = detail.includes('SUCCESS') ? 'success' : detail.includes('ERROR') ? 'error' : '';
                        html += `<li class="${className}">${detail}</li>`;
                    });
                    html += '</ul>';
                }
            }
            
            resultsDiv.innerHTML = html;
        }
        
        function clearResults() {
            document.getElementById('results').style.display = 'none';
            document.getElementById('imagePreview').innerHTML = '';
            uploadedImages = [];
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(html)


@app.post("/test-images")
async def test_images(request: Request):
    """Test image processing with the fixed FastMCP Image approach"""
    try:
        data = await request.json()
        images = data.get("images", [])
        
        results = {
            "processed_count": 0,
            "details": []
        }
        
        for i, img in enumerate(images, 1):
            try:
                # Get image data
                img_data = img.get("data")
                img_type = img.get("type", "image/png")
                img_name = img.get("name", f"image_{i}")
                
                if not img_data:
                    results["details"].append(f"Image {i}: ERROR - No data")
                    continue
                
                # Convert base64 to bytes
                if img_data.startswith('data:'):
                    img_data = img_data.split(',', 1)[1]
                img_bytes = base64.b64decode(img_data)
                
                # Determine format
                if "jpeg" in img_type or "jpg" in img_type:
                    format_str = "jpeg"
                elif "gif" in img_type:
                    format_str = "gif"
                elif "webp" in img_type:
                    format_str = "webp"
                else:
                    format_str = "png"
                
                # Create FastMCP Image object (FIXED VERSION)
                fastmcp_image = Image(data=img_bytes, format=format_str)
                
                # Validate the created object
                if hasattr(fastmcp_image, 'data') and hasattr(fastmcp_image, '_format'):
                    results["processed_count"] += 1
                    results["details"].append(
                        f"Image {i} ({img_name}): SUCCESS - "
                        f"{len(img_bytes)} bytes, {fastmcp_image._format}, {fastmcp_image._mime_type}"
                    )
                else:
                    results["details"].append(f"Image {i}: ERROR - Invalid FastMCP Image object")
                    
            except Exception as e:
                results["details"].append(f"Image {i}: ERROR - {str(e)}")
        
        return JSONResponse(results)
        
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


async def main():
    """Run the simple test server"""
    print("Simple Image Test Server for MCP Feedback Enhanced")
    print("=" * 60)
    print("Starting server on http://localhost:8772")
    print("This tests the FIXED FastMCP Image processing")
    print("Press Ctrl+C to stop")
    
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=8772,
        log_level="info"
    )
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
