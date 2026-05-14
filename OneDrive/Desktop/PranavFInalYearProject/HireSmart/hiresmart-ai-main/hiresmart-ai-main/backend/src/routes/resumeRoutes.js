const router = require('express').Router();
const multer = require('multer');
const axios = require('axios');
const fs = require('fs');
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

const upload = multer({ dest: 'src/uploads/' });

async function textFromFile(file) {
  const name = file.originalname.toLowerCase();

  // PDF Parsing
  if (name.endsWith('.pdf')) {
    try {
      const data = new Uint8Array(fs.readFileSync(file.path));

      const pdf = await pdfjsLib.getDocument({ data }).promise;

      let text = '';

      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);

        const content = await page.getTextContent();

        text +=
          content.items.map(item => item.str).join(' ') + '\n';
      }

      if (!text || text.trim().length < 10) {
        throw new Error('Could not extract readable text from PDF');
      }

      return text;

    } catch (err) {
      console.log('PDF Parse Error:', err.message);

      throw new Error(
        'PDF parsing failed. Please upload a text-based PDF.'
      );
    }
  }

  // TXT File Parsing
  return fs.readFileSync(file.path, 'utf8');
}

router.post(
  '/analyze',
  upload.single('resume'),
  async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({
          message: 'Resume file required'
        });
      }

      const resumeText = await textFromFile(req.file);

      const ai = await axios.post(
        (process.env.AI_SERVICE_URL ||
          'http://127.0.0.1:8000') + '/analyze',
        {
          resumeText,
          jobDescription:
            req.body.jobDescription || ''
        }
      );

      res.json({
        ...ai.data,
        filename: req.file.originalname
      });

    } catch (e) {
      console.log(
        'Resume analysis error:',
        e.message
      );

      res.status(500).json({
        message: 'Resume analysis failed.',
        error: e.message
      });
    }
  }
);

module.exports = router;