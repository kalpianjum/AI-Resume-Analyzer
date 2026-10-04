const express = require("express");
const cors = require("cors");
const multer = require("multer");

const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");

const app = express();
app.use(cors());
app.use(express.json());

const upload = multer({ dest: "uploads/" });

app.get("/", (req, res) => {
  res.send("Backend is running");
});

app.post("/analyze", upload.single("resume"), async (req, res) => {
  try {
    const jobDesc = req.body.jobDesc;
    const file = req.file;

    console.log("➡️ Sending to AI...");

    const formData = new FormData();
    formData.append("resume", fs.createReadStream(file.path), file.originalname);
    formData.append("jobDesc", jobDesc);

    const response = await axios.post(
      "http://127.0.0.1:5001/analyze",
      formData,
      {
        headers: formData.getHeaders(),
      }
    );

    console.log("✅ Got response from AI");

    res.json(response.data);
  } catch (error) {
    console.error("❌ ERROR:", error.message);
    res.status(500).send("Error connecting to AI");
  }
});

app.listen(5000, () => {
  console.log("Server running on port 5000");
});