# SmartScreener Bulk Upload Script

This script allows you to bulk upload all resume and job description files from the project directories to the SmartScreener database.

## Prerequisites

1. **Database Setup**: Ensure the SmartScreener application has been run at least once to create the database
2. **File Organization**:
   - Resume files should be in the `resumes/` directory
   - Job description files should be in the `job_descriptions/` directory
3. **Supported Formats**:
   - **Resumes**: PDF, DOCX, DOC
   - **Job Descriptions**: PDF, DOCX, DOC

## Usage

### Method 1: Run the Script Directly

```bash
python bulk_upload.py
```

### Method 2: Run with Python Interpreter

```bash
python3 bulk_upload.py
```

## What the Script Does

### Resume Upload Process
1. Scans the `resumes/` directory for supported file formats
2. Uploads each resume file through the application's upload endpoint
3. Performs AI analysis on each resume (if OpenAI API is configured)
4. Stores parsed resume data in the database

### Job Description Upload Process
1. Scans the `job_descriptions/` directory for supported file formats
2. Uploads each job description file through the application's upload endpoint
3. Automatically extracts job details (title, skills, requirements, education)
4. Stores parsed job description data in the database

## Output

The script provides detailed progress information:

```
🚀 SmartScreener Bulk Upload Script
==================================================
📊 Starting bulk upload process...

📄 UPLOADING RESUMES
------------------------------
📤 Uploading: John_Doe_Resume.pdf
✅ Successfully uploaded: John_Doe_Resume.pdf
📤 Uploading: Jane_Smith_CV.docx
✅ Successfully uploaded: Jane_Smith_CV.docx

💼 UPLOADING JOB DESCRIPTIONS
------------------------------
📤 Uploading: Software_Engineer_Job.pdf
✅ Successfully uploaded: Software_Engineer_Job.pdf

🎉 BULK UPLOAD COMPLETE
==================================================
📄 Total resumes processed: 2
💼 Total job descriptions processed: 1
✅ Total successful uploads: 3
⚠️  Total skipped: 0
```

## Features

- **Progress Tracking**: Shows upload progress for each file
- **Error Handling**: Continues processing even if individual files fail
- **AI Analysis**: Automatically enables AI analysis for uploaded resumes
- **Auto-Extraction**: Automatically extracts job details from uploaded job descriptions
- **Rate Limiting**: Includes delays between uploads to avoid overwhelming the system

## Troubleshooting

### Common Issues

1. **"Database not found" Error**
   - Solution: Run the Flask application first with `python app.py` to create the database

2. **"No files found" Message**
   - Solution: Ensure files are placed in the correct directories (`resumes/` and `job_descriptions/`)

3. **Upload Failures**
   - Check file formats are supported (PDF, DOCX, DOC)
   - Ensure files are not corrupted
   - Check file size limits (default: 10MB)

4. **AI Analysis Not Working**
   - Ensure OpenAI API key is configured in `.env` file
   - The script will still upload files but without AI analysis

### File Organization

Ensure your project structure looks like this:

```
SmartScreener/
├── bulk_upload.py
├── app.py
├── resumes/
│   ├── john_doe_resume.pdf
│   ├── jane_smith_cv.docx
│   └── ...
├── job_descriptions/
│   ├── software_engineer_job.pdf
│   ├── data_scientist_role.docx
│   └── ...
└── instance/
    └── smartscreener.db
```

## After Upload

Once the bulk upload is complete:

1. **Start the Web Application**: Run `python app.py`
2. **Access the Dashboard**: Open your browser to view uploaded data
3. **View Rankings**: Use the ranking features to match candidates with jobs
4. **Analytics**: Check the dashboard for insights and statistics

## Notes

- The script processes files in the order they appear in the directory
- AI analysis is enabled by default for resumes (requires OpenAI API key)
- Job descriptions are processed with auto-extraction enabled
- All uploaded data is associated with the current user session