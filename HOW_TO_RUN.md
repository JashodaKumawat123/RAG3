# 🚀 How to Run EduRAG Project - Complete Guide

## 📋 **Prerequisites Checklist**

Before starting, ensure you have:

- [ ] **Python 3.10 or higher** installed
- [ ] **Git** installed (for cloning)
- [ ] **Stable internet connection** (for downloading models)
- [ ] **At least 2GB free disk space** (for CLIP model and dependencies)

### **Check Python Version**
```bash
python --version
# Should show: Python 3.10.x or higher
```

## 🛠️ **Step-by-Step Installation**

### **Step 1: Download/Clone the Project**

**Option A: If you have the files locally**
```bash
# Navigate to your project directory
cd "C:\Users\Jashoda Kumawat\Desktop\RAG1"
```

**Option B: If you need to clone from repository**
```bash
# Navigate to your desired directory
cd "C:\Users\Jashoda Kumawat\Desktop"

# Clone the repository
git clone <repository-url> RAG1
cd RAG1
```

### **Step 2: Verify Project Structure**
```bash
# Check if all files are present
dir
# You should see:
# - app.py
# - requirements.txt
# - core/ folder
# - content/ folder
# - sample_resources.csv
# - README.md
```

### **Step 3: Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt
```

**What this installs:**
- `streamlit` - Web interface
- `chromadb` - Vector database
- `torch` - PyTorch for CLIP
- `transformers` - Hugging Face models
- `Pillow` - Image processing
- `opencv-python` - Video processing
- `pandas` - Data manipulation

**Expected output:**
```
Collecting streamlit...
Collecting chromadb...
Collecting torch...
...
Successfully installed streamlit-x.x.x chromadb-x.x.x torch-x.x.x ...
```

### **Step 4: Run the Application**
```bash
# Start the Streamlit app
streamlit run app.py
```

**Expected output:**
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://xxx.xxx.xxx.xxx:8501
External URL: http://xxx.xxx.xxx.xxx:8501
```

### **Step 5: Access the Application**
1. Open your web browser
2. Go to: `http://localhost:8501`
3. You should see the EduRAG interface with 7 tabs

## 🎯 **First-Time Setup & Testing**

### **Phase 1: Basic Setup (5 minutes)**

#### **1.1 Ingest Sample Content**
1. In the app, go to **"Ingest"** tab
2. Click **"Choose Files"** under "CSV of resources"
3. Select `sample_resources.csv` from your project folder
4. Click **"Ingest CSV"**
5. **Expected result**: "Ingested 6 text chunks into Chroma"

#### **1.2 Test Learning Path**
1. Go to **"Learning Path"** tab
2. In the sidebar, set your preferences:
   - **Student Level**: Beginner
   - **Learning Style**: Visual
   - **Target Competencies**: Select "arrays", "linked-lists", "trees"
3. Click **"Save Profile"**
4. **Expected result**: Table showing sequenced competencies with prerequisites

#### **1.3 Test RAG Query**
1. Go to **"Ask (RAG)"** tab
2. Type: "What are arrays?"
3. Set **Top-k** to 3
4. Click **"Search & Answer"**
5. **Expected result**: Retrieved context and draft answer

### **Phase 2: Quiz & Analytics (5 minutes)**

#### **2.1 Take a Quiz**
1. Go to **"Quiz"** tab
2. Select **"Arrays Basics Quiz"**
3. Answer all 3 questions
4. Click **"Submit Quiz"**
5. **Expected result**: Score display and remediation suggestions

#### **2.2 Check Progress Analytics**
1. Go to **"Progress"** tab
2. **Expected results**:
   - Mastery bar chart showing competency levels
   - Performance prediction metrics
   - Knowledge gaps (if any)
   - Progress history table

### **Phase 3: Multimodal Features (Optional - 10 minutes)**

#### **3.1 Upload Images/Videos**
1. Go to **"Ingest"** tab
2. Under **"Multimodal Uploads"**:
   - Upload some PNG/JPG images
   - Select competencies (e.g., "arrays")
   - Click **"Ingest Media"**
3. **Expected result**: "Media indexed: X (images/frames)"

#### **3.2 Test Cross-modal Search**
1. Go to **"Cross-modal Search"** tab
2. Type: "binary tree diagram"
3. Click **"Search Media"**
4. **Expected result**: Metadata of matching images/video frames

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **Issue 1: "Module not found" errors**
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

#### **Issue 2: Port 8501 already in use**
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502

# Or kill the process using port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### **Issue 3: CLIP model download fails**
```bash
# Solution: Check internet and try again
# The model downloads automatically on first use
# Look for progress messages in terminal
```

#### **Issue 4: ChromaDB errors**
```bash
# Solution: Clear ChromaDB cache
rmdir /s chroma_store
# Restart the app - it will recreate the database
```

#### **Issue 5: Memory issues with large files**
```bash
# Solution: Use smaller files or increase system memory
# For videos, the system limits to 20 frames per video
```

### **Performance Optimization**

#### **For Better Speed:**
```bash
# Use GPU if available (automatic detection)
# The app will show "Using CUDA" in terminal if GPU is available

# For CPU-only systems:
# - Limit video file sizes
# - Process images in smaller batches
# - Close other applications to free memory
```

#### **For Production:**
```bash
# Set environment variables
set CHROMA_DIR=C:\path\to\persistent\storage

# Run with production settings
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

## 📊 **Verification Checklist**

### **✅ Basic Functionality**
- [ ] App opens at `http://localhost:8501`
- [ ] All 7 tabs are visible
- [ ] Sidebar shows user settings
- [ ] No error messages in browser console

### **✅ Content Ingestion**
- [ ] CSV upload works
- [ ] "Ingested X text chunks" message appears
- [ ] No file processing errors

### **✅ Learning Path**
- [ ] Competencies are sequenced correctly
- [ ] Prerequisites are shown
- [ ] Objectives are displayed
- [ ] Difficulty recommendations appear

### **✅ RAG Functionality**
- [ ] Text queries return results
- [ ] Context is retrieved
- [ ] Draft answers are generated
- [ ] Metadata is displayed

### **✅ Quiz System**
- [ ] Quiz packs are loaded
- [ ] Questions display correctly
- [ ] Grading works
- [ ] Scores are calculated
- [ ] Remediation suggestions appear

### **✅ Progress Tracking**
- [ ] Mastery chart displays
- [ ] Performance predictions show
- [ ] Gap detection works
- [ ] Progress history is logged

### **✅ Multimodal Features**
- [ ] Image upload works
- [ ] Video frame extraction functions
- [ ] Cross-modal search returns results
- [ ] Metadata is properly tagged

## 🎯 **Quick Test Commands**

### **Test Core Modules**
```bash
# Test all core functionality
python test_multimodal.py
```

### **Test Individual Components**
```bash
# Test imports
python -c "import core.rag, core.mm, core.quizzes; print('All modules imported successfully')"

# Test quiz loading
python -c "from core.quizzes import load_quiz_packs; print(f'Found {len(load_quiz_packs())} quiz packs')"

# Test database
python -c "from core.user import init_db; init_db(); print('Database initialized')"
```

## 📱 **Mobile/Remote Access**

### **Access from Other Devices**
```bash
# Find your computer's IP address
ipconfig

# Use the Network URL shown in terminal
# Example: http://192.168.1.100:8501
```

### **Access from Internet (Advanced)**
```bash
# Use ngrok for temporary public access
pip install pyngrok
ngrok http 8501
# Use the ngrok URL provided
```

## 🔄 **Restart & Maintenance**

### **Daily Usage**
```bash
# Start the app
streamlit run app.py

# Keep terminal open while using
# Use Ctrl+C to stop when done
```

### **After Updates**
```bash
# Pull latest changes
git pull

# Reinstall if requirements changed
pip install -r requirements.txt

# Restart the app
streamlit run app.py
```

### **Clean Restart**
```bash
# Stop the app (Ctrl+C)
# Clear temporary files
del /q tmp_*
# Restart
streamlit run app.py
```

## 📞 **Getting Help**

### **If Something Doesn't Work:**

1. **Check the terminal** for error messages
2. **Check browser console** (F12) for JavaScript errors
3. **Verify file structure** matches the expected layout
4. **Test with sample data** first before adding your own content
5. **Check system requirements** (Python version, memory, disk space)

### **Common Success Patterns:**
- ✅ First run: 5-10 minutes for model downloads
- ✅ Subsequent runs: 30 seconds to start
- ✅ Quiz scores: Update immediately in Progress tab
- ✅ File uploads: Show success messages
- ✅ Search results: Return within 2-3 seconds

---

## 🎉 **You're Ready!**

Once you've completed the verification checklist, you have a fully functional EduRAG system running locally. You can now:

- **Add your own content** via the Ingest tab
- **Create custom quizzes** by adding JSON files to `content/quizzes/`
- **Extend competencies** by modifying `core/competency.py`
- **Customize the UI** by editing `app.py`
- **Deploy to production** using the deployment options in the main README

**Happy learning! 🚀**
