# 🚀 EduRAG Quick Start Guide

Get EduRAG running in **5 minutes**!

## ⚡ Super Quick Start

```bash
# 1. Clone and setup (one command!)
git clone <your-repo> && cd EduRAG && python setup.py

# 2. Run the app
streamlit run app.py

# 3. Open http://localhost:8501
```

That's it! 🎉

## 📋 What You Get

✅ **Complete RAG System** - Intelligent content retrieval and generation  
✅ **Personalized Learning** - Adaptive paths based on your progress  
✅ **Modern UI** - Beautiful Streamlit interface  
✅ **DSA Content** - Ready-to-use Data Structures & Algorithms materials  
✅ **Learning Analytics** - Track your progress and mastery  

## 🎯 First Steps

1. **Take Learning Style Assessment** (Settings → Learning Style Assessment)
2. **Generate Your Learning Path** (Dashboard → Generate New Learning Path)
3. **Ask Questions** (Ask Questions → Try "What is an array?")
4. **Take Practice Quizzes** (Quiz → Choose a topic)

## 🔧 Customization

### Add Your Own Content
```bash
# Add notes
echo "# My Topic" > content/notes/my_topic.md

# Add videos
# Edit content/videos/links.json

# Re-index content
python data_ingest.py --content_dir content --persist_dir storage/chroma
```

### Change Domain
1. Edit `models/skills.yaml` - Define your topic graph
2. Replace content in `content/` directory
3. Update prompts in `models/prompts.yaml`

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Hugging Face Spaces
1. Create new Space
2. Upload code
3. Add `requirements.txt`
4. Deploy!

### Docker
```bash
docker build -t eduragg .
docker run -p 8501:8501 eduragg
```

## 🧪 Testing

```bash
# Run demo
python demo.py

# Run evaluation
python eval_rag.py --output results.json
```

## 📞 Need Help?

- **Issues**: GitHub Issues
- **Docs**: README.md
- **Demo**: `python demo.py`

---

**Ready to revolutionize learning? Start with EduRAG! 🎓**