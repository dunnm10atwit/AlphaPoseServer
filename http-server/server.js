const express = require('express');
const https = require('https');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { exec } = require('child_process');

var key = fs.readFileSync('/etc/letsencrypt/live/brezzy.us/privkey.pem');
var cert = fs.readFileSync('/etc/letsencrypt/live/brezzy.us/fullchain.pem');
var options = {
  key: key,
  cert: cert
};

const app = express();
const port = 443;
var server = https.createServer(options, app);

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
 req.setTimeout(500000, function(){console.log('Connection timeout'); return;});
 console.log('uploading video');
 const allowedFormats = ['.mp4', '.avi', '.mkv', 'mov', '.MOV', '.MP4', '.3gp'];
  const fileExtension = path.extname(req.file.originalname);

  // Check if the uploaded file is a video
  if (allowedFormats.includes(fileExtension)) {
    const inputFilePath = path.join('/home/jakebres/AlphaPoseServer/http-server/uploads', req.file.originalname);
    const outputFilePathTemp = path.join('/home/jakebres/AlphaPoseServer/AlphaPose/examples/res/', 'AlphaPose_' +  req.file.originalname);
    const outputFilePath = outputFilePathTemp.slice(0, -3) + 'mp4';
    const barpath_outputFilePath = path.join('/home/jakebres/AlphaPoseServer/', 'Barpath_AlphaPose_' + req.file.originalname);
    const barpath_outputFilePathVid = barpath_outputFilePath.slice(0, -3) + 'mp4';
    const barpath_outputFilePathImg = barpath_outputFilePath.slice(0, -3) + 'png';
    const combined_output_path = path.join('/home/jakebres/AlphaPoseServer/', 'Combined_Barpath_AlphaPose_' + req.file.originalname);
    const combined_vid_path = combined_output_path.slice(0, -3) + 'mp4';

    // Run the Python command with absolute paths
    const pythonCommand = '/opt/conda/bin/python process_video.py --cfg configs/halpe_26/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/halpe26_fast_res50_256x192.pth --video ' + inputFilePath + ' --save_video';

    console.log('Processing Video');
    exec(pythonCommand, { cwd: '/home/jakebres/AlphaPoseServer/AlphaPose' }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error during command execution: ${error.message}`);
        res.status(500).send('Internal Server Error');
        return;
      }

      console.log(`Command output: ${stdout}`);
      console.error(`Command error: ${stderr}`);


    // Run the Python command with absolute paths
    const pythonCommand_bar = '/opt/conda/bin/python track_barbell.py ' + outputFilePath;
    const pythonCommand_merge = '/opt/conda/bin/python vid_merger.py ' + barpath_outputFilePathVid + ' ' + barpath_outputFilePathImg;

    console.log('Tracking Barbell...');
    exec(pythonCommand_bar, { cwd: '/home/jakebres/AlphaPoseServer' }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error during command execution: ${error.message}`);
        res.status(500).send('Internal Server Error');
        return;
      }

      console.log(`Command output: ${stdout}`);
      console.error(`Command error: ${stderr}`);

        exec(pythonCommand_merge, {cwd: '/home/jakebres/AlphaPoseServer' }, (error, stdout, stderr) => {
            if (error) {
            console.error(`Error during command execution: ${error.message}`);
            res.status(500).send('Internal Server Error');
            return;
            }

            console.log(`Command output: ${stdout}`);
            console.error(`Command error: ${stderr}`);

            // Provide the processed video for download
            fs.stat(combined_vid_path, (err, stats) => {
            if (err) {
                console.error(err);
                res.status(500).send('Internal Server Error');
            } else {
                res.setHeader('Content-Type', 'application/octet-stream');
                res.setHeader('Content-Disposition', 'attachment; filename=Combined_' + req.file.originalname);
                res.setHeader('Content-Length', stats.size);
                res.sendFile(combined_vid_path, (err) => {
                if (err) {
                    console.error(err);
                    res.status(500).send('Internal Server Error');
                } else {
                    console.log('Succesfully sent barpath vid');
                    // Remove the files after output
                    fs.unlinkSync(barpath_outputFilePathVid);  // barpath vid
                    fs.unlinkSync(barpath_outputFilePathImg);  // barpath trace
                    fs.unlinkSync(combined_vid_path);  // returned vid
                    fs.unlinkSync(inputFilePath);  // original vid
                    fs.unlinkSync(outputFilePath);  // AlphaPose result
                    // res.status(200).send('File upload, processing, and download complete');
               }
          });
         }
       });
    });
    console.log('Done tracking barbell.');
    });
    return;
    });

  } else {
    // File format not supported
    res.status(400).send('Unsupported file format. Please upload a video file.');
  }
});

app.use('/home/jakebres/AlphaPoseServer/http-server/uploads', express.static('uploads'));

server.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
