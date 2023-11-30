const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

const app = express();
const port = 80;

const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, '/home/jakebres/AlphaPoseServer/http-server/uploads');
  },
  filename: (req, file, cb) => {
    cb(null, file.originalname);
  },
});

const upload = multer({ storage: storage });

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.post('/upload', upload.single('file'), (req, res) => {
  const allowedFormats = ['.mp4', '.avi', '.mkv', 'mov', '.txt', '.bz2'];
  const fileExtension = path.extname(req.file.originalname);

  // Check if the uploaded file is a video
  if (allowedFormats.includes(fileExtension)) {
    const inputFilePath = path.join('/home/jakebres/AlphaPoseServer/http-server/uploads', req.file.originalname);
    const outputFilePath = path.join('/home/jakebres/AlphaPoseServer/AlphaPose/examples/res/', 'AlphaPose_' +  req.file.originalname);

    // Run the Python command with absolute paths
    const pythonCommand = '/opt/conda/bin/python process_video.py --cfg configs/halpe_26/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/halpe26_fast_res50_256x192.pth --video ' + inputFilePath + ' --save_video';

    exec(pythonCommand, { cwd: '/home/jakebres/AlphaPoseServer/AlphaPose' }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error during command execution: ${error.message}`);
        res.status(500).send('Internal Server Error');
        return;
      }

      console.log(`Command output: ${stdout}`);
      console.error(`Command error: ${stderr}`);

      // Provide the processed video for download
      res.download(outputFilePath, 'AlphaPose_'+ req.file.originalname, (err) => {
        if (err) {
          console.error(err);
          res.status(500).send('Internal Server Error');
        } else {
          // Remove the original file after successful download
          fs.unlinkSync(inputFilePath);
        }
      });
    });
  } else {
    // File format not supported
    res.status(400).send('Unsupported file format. Please upload a video file.');
  }
});

app.use('/home/jakebres/AlphaPoseServer/http-server/uploads', express.static('uploads'));

app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
