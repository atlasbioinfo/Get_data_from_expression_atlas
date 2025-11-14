# Multi-Turn Conversation Example

This document demonstrates the new multi-turn conversation flow in `smart_chat.py`.

## Example 1: Complete Workflow

### Step 1: User Query
```
💬 You: I need Arabidopsis leaf data
```

**System Response:**
```
🔍 Understanding your needs:
  • Species: arabidopsis thaliana
  • Keywords: leaf
  • Experiment type: baseline

🎯 Found 3 matching experiments:
================================================================================

  [1] E-GEOD-38612 (similarity: 42.89%)
      Species: Arabidopsis thaliana
      Type: baseline
      Description: Baseline expression across fruit, leaf, flower

  [2] E-GEOD-55866 (similarity: 26.88%)
      Species: Arabidopsis thaliana
      Type: baseline
      Description: Baseline expression across silique

  [3] E-MTAB-7978 (similarity: 26.32%)
      Species: Arabidopsis thaliana
      Type: baseline
      Description: Baseline expression across adult vascular leaf, petal, rosette leaf

================================================================================
💬 Which experiment would you like to explore?
   Type 1, 2, or 3 to select
   Type 'back' or 'new' to start a new search
```

### Step 2: User Selection
```
💬 You: 1
```

**System Response:**
```
✅ You selected: E-GEOD-38612

📊 Experiment details:
  Experiment ID: E-GEOD-38612
  Experiment page: https://www.ebi.ac.uk/gxa/experiments/E-GEOD-38612

🔎 Browsing FTP directory...
  ✓ Found 45 files
  FTP URL: https://ftp.ebi.ac.uk/pub/databases/microarray/data/atlas/experiments/E-GEOD-38612/

🧠 Intelligently identifying gene expression data files...

  TPMS files:
    • E-GEOD-38612-tpms.tsv
    • E-GEOD-38612-tpms-markers.tsv

  FPKMS files:
    • E-GEOD-38612-fpkms.tsv

================================================================================
🎯 Recommended download:
================================================================================
  File: E-GEOD-38612-tpms.tsv
  Size: 1234567 bytes
  URL: https://ftp.ebi.ac.uk/pub/.../E-GEOD-38612-tpms.tsv

================================================================================
💬 Would you like to download this data?
   Type 'yes' to download
   Type 'no' or 'skip' to see manual download guide
   Type 'back' to select a different experiment
```

### Step 3a: User Confirms Download
```
💬 You: yes
```

**System Response:**
```
📥 Starting download...

✅ Download successful!
  Saved to: ./expression_atlas_data
    • tpms: expression_atlas_data/E-GEOD-38612-tpms.tsv
    • fpkms: expression_atlas_data/E-GEOD-38612-fpkms.tsv
    • condensed-sdrf: expression_atlas_data/E-GEOD-38612.condensed-sdrf.tsv

📊 Next step: Data Analysis
[Analysis guide provided...]
```

### Step 3b: User Declines Download
```
💬 You: no
```

**System Response:**
```
Skipping download...

📖 Manual Download Guide
================================================================================
1. Visit the experiment page:
   https://www.ebi.ac.uk/gxa/experiments/E-GEOD-38612

2. Click the 'Downloads' tab

3. Download the files you need:
   • TPM (Transcripts Per Million) - recommended
   • FPKM (Fragments Per Kilobase Million)
   • Raw counts
```

### Step 3c: User Goes Back
```
💬 You: back
```

**System Response:**
```
🔄 Going back to experiment selection...

🎯 Found 3 matching experiments:
[Shows recommendation list again...]
```

---

## Example 2: Direct Experiment ID

### User Query
```
💬 You: Download E-CURD-1
```

**System Response:**
```
🔍 Understanding your needs:
  • Experiment ID: E-CURD-1

📊 Experiment details:
  Experiment ID: E-CURD-1
  Experiment page: https://www.ebi.ac.uk/gxa/experiments/E-CURD-1

[Shows FTP files and download prompt...]
```

---

## Example 3: Starting New Search

### At Any Point, User Can Type:
```
💬 You: new
```
or
```
💬 You: back
```

**System Response:**
```
🔄 Starting new search...
```

---

## Conversation States

The system maintains these states:

1. **INITIAL**: Waiting for user query
2. **SELECTING**: User is selecting from recommendations (1/2/3)
3. **CONFIRMING**: User is confirming download (yes/no)

At any stage, users can:
- Type numbers (1, 2, 3) to select experiments
- Type 'back' or 'new' to restart
- Type 'yes' to confirm downloads
- Type 'no' or 'skip' to decline downloads
- Type 'quit' or 'exit' to exit the program

---

## Key Features

✅ **No automatic decisions** - User approves each step
✅ **Top-3 recommendations** - Vector search finds best matches
✅ **Full control** - Go back at any time
✅ **Clear prompts** - System tells you what to type next
✅ **Stateful conversation** - Remembers context across turns
